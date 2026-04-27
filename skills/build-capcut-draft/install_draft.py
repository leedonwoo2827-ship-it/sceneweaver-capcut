"""
sceneweaver-capcut v0.2.0 - 자동 설치

build_draft.py 가 만든 workspace/ch{NN}/draft/ 를
%LOCALAPPDATA%\\CapCut\\User Data\\Projects\\com.lveditor.draft\\ 로 복사 +
root_meta_info.json 에 새 엔트리 등록 (자동 백업).

CapCut 의 전역 드래프트 레지스트리(`root_meta_info.json`) 갱신이 핵심:
- `all_draft_store[]` 에 새 엔트리 append (~30개 필드)
- `draft_ids` += 1
이게 빠지면 폴더만 복사돼도 CapCut 목록에 안 뜸.

사용:
    python install_draft.py 02
    python install_draft.py 02 --overwrite
    python install_draft.py 02 --target-root <CUSTOM_PATH>     # 디버깅용
"""

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path


# ─── 헬퍼 ──────────────────────────────────────────────
def now_us() -> int:
    return int(time.time() * 1_000_000)


def localappdata_capcut_root() -> Path:
    """CapCut 의 com.lveditor.draft 디렉터리 경로."""
    base = os.environ.get("LOCALAPPDATA")
    if not base:
        raise RuntimeError("LOCALAPPDATA 환경변수가 설정되지 않음 (Windows 만 지원)")
    return Path(base) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"


# ─── root_meta_info.json 엔트리 빌더 ────────────────────
def build_registry_entry(draft_name: str, draft_fold_path: str, draft_root_path: str,
                         draft_id: str, materials_size: int,
                         duration_us: int, create_time_us: int) -> dict:
    """root_meta_info.json 의 all_draft_store[] 에 들어갈 엔트리.

    필드 셋은 사용자 PC 의 정상 드래프트 (`0427`, `ch02_draft_20260427`) 진단 데이터로
    정확히 확보. 모든 default 값 보존.
    """
    return {
        "cloud_draft_cover": False,
        "cloud_draft_sync": False,
        "draft_cloud_last_action_download": False,
        "draft_cloud_purchase_info": "",
        "draft_cloud_template_id": "",
        "draft_cloud_tutorial_info": "",
        "draft_cloud_videocut_purchase_info": "",
        "draft_cover": f"{draft_fold_path}\\draft_cover.jpg",
        "draft_fold_path": draft_fold_path,
        "draft_id": draft_id,
        "draft_is_ai_shorts": False,
        "draft_is_cloud_temp_draft": False,
        "draft_is_invisible": False,
        "draft_is_web_article_video": False,
        "draft_json_file": f"{draft_fold_path}\\draft_content.json",
        "draft_name": draft_name,
        "draft_new_version": "",
        "draft_root_path": draft_root_path,
        "draft_timeline_materials_size": materials_size,
        "draft_type": "",
        "draft_web_article_video_enter_from": "",
        "streaming_edit_draft_ready": True,
        "tm_draft_cloud_completed": "",
        "tm_draft_cloud_entry_id": -1,
        "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1,
        "tm_draft_cloud_space_id": -1,
        "tm_draft_cloud_user_id": -1,
        "tm_draft_create": create_time_us,
        "tm_draft_modified": create_time_us,
        "tm_draft_removed": 0,
        "tm_duration": duration_us,
    }


def update_root_meta_info(root_meta_path: Path, entry: dict, root_path_str: str) -> Path:
    """root_meta_info.json 갱신. 백업 경로 반환.

    - 없으면 새로 생성
    - 있으면 백업 후 entry append + draft_ids 증가
    """
    backup_path = root_meta_path.with_suffix(
        f".json.bak.{time.strftime('%Y%m%d_%H%M%S')}")

    if root_meta_path.exists():
        shutil.copy2(root_meta_path, backup_path)
        with root_meta_path.open(encoding="utf-8") as f:
            data = json.load(f)
        # 기존 동일 draft_id 가 있으면 제거 (재설치 케이스)
        before = len(data.get("all_draft_store", []))
        data["all_draft_store"] = [e for e in data.get("all_draft_store", [])
                                    if e.get("draft_id") != entry["draft_id"]]
        removed = before - len(data["all_draft_store"])
        if removed:
            print(f"[info] 기존 동일 draft_id 엔트리 {removed}개 제거 (재설치)")
    else:
        data = {"all_draft_store": [], "draft_ids": 0, "root_path": root_path_str}
        # 백업할 게 없으면 backup_path 생성 안 함
        backup_path = None  # type: ignore

    data["all_draft_store"].append(entry)
    data["draft_ids"] = len(data["all_draft_store"])
    data.setdefault("root_path", root_path_str)

    with root_meta_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    return backup_path  # type: ignore


# ─── 폴더 복사 ─────────────────────────────────────────
def install_folder(src: Path, dst: Path, overwrite: bool) -> None:
    if dst.exists():
        if not overwrite:
            raise FileExistsError(
                f"이미 존재함: {dst}\n"
                f"  → 덮어쓰려면 --overwrite 옵션 추가")
        print(f"[warn] 기존 폴더 삭제 후 재설치: {dst}")
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"[info] 폴더 복사 완료: {dst}")


# ─── 메인 ──────────────────────────────────────────────
def install(workspace: Path, target_root: Path, overwrite: bool) -> dict:
    """빌드된 draft/ 를 CapCut 디렉터리로 설치 + 레지스트리 등록.

    workspace/ch{NN}/draft/ 가 있어야 함 (build_draft.py 출력).
    """
    src_draft = workspace / "draft"
    if not src_draft.is_dir():
        raise FileNotFoundError(
            f"draft/ 폴더 없음: {src_draft}\n"
            f"  → 먼저 build_draft.py 실행")

    meta_path = src_draft / "draft_meta_info.json"
    content_path = src_draft / "draft_content.json"
    if not (meta_path.is_file() and content_path.is_file()):
        raise FileNotFoundError(
            f"draft_meta_info.json 또는 draft_content.json 없음: {src_draft}")

    # CapCut 디렉터리 존재 확인
    if not target_root.is_dir():
        raise FileNotFoundError(
            f"\n  CapCut 디렉터리가 없습니다: {target_root}\n"
            f"  → CapCut 을 한 번 실행해서 아무 프로젝트라도 저장 후 재시도하세요.\n"
            f"  → 자세한 안내: docs/OTHER-PC-SETUP.md")

    # 메타 로드
    with meta_path.open(encoding="utf-8") as f:
        meta = json.load(f)
    draft_id = meta["draft_id"]
    draft_name = meta["draft_name"]
    materials_size = meta.get("draft_timeline_materials_size_",
                              meta.get("draft_timeline_materials_size", 0))

    # content 에서 duration 추출
    with content_path.open(encoding="utf-8") as f:
        content = json.load(f)
    duration_us = content.get("duration", 0)

    # 대상 경로 계산
    target_dir = target_root / draft_name
    draft_fold_path = str(target_dir).replace("/", "\\")
    draft_root_path = str(target_root).replace("/", "\\")

    # 폴더 복사
    install_folder(src_draft, target_dir, overwrite)

    # draft_meta_info.json 의 경로 필드들을 실제 설치 위치로 갱신
    # CapCut 은 draft_fold_path / draft_root_path 가 실제 위치와 일치해야 함
    installed_meta_path = target_dir / "draft_meta_info.json"
    with installed_meta_path.open(encoding="utf-8") as f:
        installed_meta = json.load(f)
    installed_meta["draft_fold_path"] = draft_fold_path.replace("\\", "/")
    installed_meta["draft_root_path"] = draft_root_path
    # draft_materials 의 file_Path 들도 실제 위치로 갱신
    for bucket in installed_meta.get("draft_materials", []):
        for item in bucket.get("value", []):
            if "file_Path" in item:
                # 기존 경로의 마지막 'Resources/...' 부분만 추출해서 새 경로로 결합
                old = item["file_Path"]
                idx = old.find("/Resources/")
                if idx >= 0:
                    item["file_Path"] = (draft_fold_path.replace("\\", "/")
                                         + old[idx:])
    with installed_meta_path.open("w", encoding="utf-8") as f:
        json.dump(installed_meta, f, ensure_ascii=False, separators=(",", ":"))

    # draft_content.json 의 자료 path 들도 갱신
    installed_content_path = target_dir / "draft_content.json"
    with installed_content_path.open(encoding="utf-8") as f:
        installed_content = json.load(f)
    for cat in ("videos", "audios"):
        for item in installed_content.get("materials", {}).get(cat, []):
            if "path" in item:
                old = item["path"]
                idx = old.find("/Resources/")
                if idx >= 0:
                    item["path"] = (draft_fold_path.replace("\\", "/")
                                    + old[idx:])
    with installed_content_path.open("w", encoding="utf-8") as f:
        json.dump(installed_content, f, ensure_ascii=False, separators=(",", ":"))

    print(f"[info] draft_content.json / draft_meta_info.json 의 경로 필드 갱신 완료")

    # root_meta_info.json 갱신
    root_meta_path = target_root / "root_meta_info.json"
    entry = build_registry_entry(
        draft_name=draft_name,
        draft_fold_path=draft_fold_path.replace("\\", "/"),
        draft_root_path=draft_root_path,
        draft_id=draft_id,
        materials_size=materials_size,
        duration_us=duration_us,
        create_time_us=now_us(),
    )
    backup = update_root_meta_info(root_meta_path, entry,
                                   draft_root_path.replace("\\", "/"))
    if backup:
        print(f"[info] root_meta_info.json 백업: {backup.name}")
    print(f"[info] root_meta_info.json 갱신: all_draft_store 에 '{draft_name}' 추가")

    return {
        "draft_id": draft_id, "draft_name": draft_name,
        "installed_to": str(target_dir),
        "registry_backup": str(backup) if backup else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="빌드된 CapCut 드래프트를 설치 + root_meta_info 갱신")
    parser.add_argument("chapter", help="챕터 번호 (예: 02)")
    parser.add_argument("--workspace", default=None,
                        help="workspace 루트 (default: ./workspace)")
    parser.add_argument("--target-root", default=None,
                        help="설치 대상 (default: %%LOCALAPPDATA%%/CapCut/.../com.lveditor.draft)")
    parser.add_argument("--overwrite", action="store_true",
                        help="기존 동명 폴더 덮어쓰기")
    args = parser.parse_args()

    chapter = args.chapter.zfill(2)
    ws_root = Path(args.workspace) if args.workspace else Path.cwd() / "workspace"
    workspace = ws_root / f"ch{chapter}"

    target_root = (Path(args.target_root) if args.target_root
                   else localappdata_capcut_root())

    try:
        result = install(workspace, target_root, args.overwrite)
    except (FileNotFoundError, FileExistsError) as e:
        print(f"[error] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[error] {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    print(f"\n[ok] 설치 완료")
    print(f"     이름: {result['draft_name']}")
    print(f"     위치: {result['installed_to']}")
    print(f"\n다음 단계:")
    print(f"  1. CapCut 완전 종료 (작업관리자에서 CapCut.exe 프로세스도 종료)")
    print(f"  2. CapCut 재실행 → 프로젝트 목록에 '{result['draft_name']}' 보임")
    print(f"  3. 더블클릭 → 자동 배치된 영상·음성 확인")
    return 0


if __name__ == "__main__":
    sys.exit(main())
