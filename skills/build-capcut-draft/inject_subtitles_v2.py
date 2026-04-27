"""
sceneweaver-capcut v0.2.0 - 자막 트랙 자동 주입 (v2)

build_draft.py 가 만든 드래프트(자막 없음) 또는 install_draft.py 가 설치한 드래프트에
SRT 자막 트랙을 추가한다.

v1 (inject_subtitles.py) 이 CapCut 8.5.0 에서 거부당한 후, 정상 작동하는 ch01 의
자막 트랙과 deep-diff 한 결과 정확히 5개 필드 값만 다름이 확인됨:

| 위치             | 필드                | v1 (깨짐)  | v2 (정상, ch01 기준) |
|------------------|---------------------|-----------|---------------------|
| text material    | check_flag          | 7         | 23                  |
| text material    | background_alpha    | 1.0       | 0.5                 |
| text material    | background_color    | ""        | "#000000"           |
| text material    | background_style    | 0         | 1                   |
| segment          | track_render_index  | 1         | 2                   |

v2 는 위 값을 ch01 정상 동작 기준으로 박아둠.

사용:
    # 1. workspace 의 SRT 를 자동 탐지해서 빌드된 draft 에 주입
    python inject_subtitles_v2.py 02

    # 2. 명시적 SRT / 드래프트 경로
    python inject_subtitles_v2.py --draft <DRAFT_DIR> --srt <SRT_PATH>

    # 3. 폰트 변경 (default: malgun.ttf)
    python inject_subtitles_v2.py 02 --font "C:/Windows/Fonts/NanumGothic.ttf"
"""

import argparse
import json
import re
import shutil
import sys
import uuid
from pathlib import Path


DEFAULT_FONT_PATH = "C:/Windows/Fonts/malgun.ttf"


# ─── 헬퍼 ──────────────────────────────────────────────
def gen_uuid() -> str:
    """CapCut 형식 UUID — 표준 36자리 (8-4-4-4-12), 4번째 그룹만 소문자."""
    u = str(uuid.uuid4()).upper()
    return u[:19] + u[19:23].lower() + u[23:]


def parse_srt(path: Path) -> list[dict]:
    """SRT → [{start_us, duration_us, text}, ...]. UTF-8 BOM / LF/CRLF 모두 허용."""
    raw = path.read_bytes().decode("utf-8-sig")
    blocks = re.split(r"\r?\n\r?\n+", raw.strip())
    cues = []
    ts_re = re.compile(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*"
                       r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})")
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue
        ts_idx = 0 if ts_re.search(lines[0]) else 1
        m = ts_re.search(lines[ts_idx])
        if not m:
            continue
        h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, m.groups())
        start_us = (h1 * 3600 + m1 * 60 + s1) * 1_000_000 + ms1 * 1000
        end_us = (h2 * 3600 + m2 * 60 + s2) * 1_000_000 + ms2 * 1000
        text = "\n".join(lines[ts_idx + 1:]).strip()
        if not text:
            continue
        cues.append({"start_us": start_us, "duration_us": end_us - start_us,
                     "text": text})
    return cues


# ─── 자막 자료 + segment 빌더 (ch01 정상 형식 기반) ─────
def make_text_material(text_id: str, text: str, group_id: str, font_path: str) -> dict:
    """자막 text material. ch01 정상 동작 형식 기반.

    v1 대비 변경된 필드 (ch01 정상값으로 보정):
    - check_flag: 7 → 23
    - background_alpha: 1.0 → 0.5
    - background_color: "" → "#000000"
    - background_style: 0 → 1
    """
    content = json.dumps({
        "styles": [{
            "fill": {"alpha": 1.0,
                     "content": {"render_type": "solid",
                                 "solid": {"alpha": 1.0,
                                           "color": [1.0, 1.0, 1.0]}}},
            "font": {"id": "", "path": font_path},
            "range": [0, len(text)],
            "size": 5.0,
        }],
        "text": text,
    }, ensure_ascii=False)

    return {
        "recognize_task_id": "", "id": text_id, "name": "",
        "recognize_text": "", "recognize_model": "", "punc_model": "",
        "type": "subtitle", "content": content, "base_content": "",
        "words": {"start_time": [], "end_time": [], "text": []},
        "current_words": {"start_time": [], "end_time": [], "text": []},
        "global_alpha": 1.0,
        "combo_info": {"text_templates": []},
        "caption_template_info": {"resource_id": "", "third_resource_id": "",
                                  "resource_name": "", "category_id": "",
                                  "category_name": "", "effect_id": "",
                                  "request_id": "", "path": "", "is_new": False,
                                  "source_platform": 0},
        "layer_weight": 1, "letter_spacing": 0.0, "text_curve": None,
        "text_loop_on_path": False, "offset_on_path": 0.0,
        "enable_path_typesetting": False, "text_exceeds_path_process_type": 0,
        "text_typesetting_paths": None, "text_typesetting_paths_file": "",
        "text_typesetting_path_index": 0,
        "line_spacing": 0.02, "has_shadow": False, "shadow_color": "",
        "shadow_alpha": 0.9, "shadow_smoothing": 0.45, "shadow_distance": 5.0,
        "shadow_point": {"x": 0.6363961030678928, "y": -0.6363961030678928},
        "shadow_angle": -45.0,
        "shadow_thickness_projection_enable": False,
        "shadow_thickness_projection_angle": 0.0,
        "shadow_thickness_projection_distance": 0.0,
        "border_alpha": 1.0, "border_color": "", "border_width": 0.08,
        "border_mode": 0, "style_name": "",
        "text_color": "#FFFFFF", "text_alpha": 1.0,
        "font_name": "", "font_title": "none", "font_size": 5.0,
        "font_path": font_path, "font_id": "", "font_resource_id": "",
        "initial_scale": 1.0, "font_url": "", "typesetting": 0,
        "alignment": 1, "line_feed": 1,
        "use_effect_default_color": True, "is_rich_text": False,
        "shape_clip_x": False, "shape_clip_y": False, "ktv_color": "",
        "text_to_audio_ids": [], "bold_width": 0.0, "italic_degree": 0,
        "underline": False, "underline_width": 0.05, "underline_offset": 0.22,
        "sub_type": 0,
        "check_flag": 23,                    # ★ v1=7 → v2=23
        "text_size": 30, "font_category_name": "", "font_source_platform": 0,
        "font_third_resource_id": "", "font_category_id": "",
        "add_type": 2, "operation_type": 0, "recognize_type": 0, "fonts": [],
        "background_color": "#000000",       # ★ v1="" → v2="#000000"
        "background_alpha": 0.5,             # ★ v1=1.0 → v2=0.5
        "background_style": 1,               # ★ v1=0 → v2=1
        "background_round_radius": 0.0,
        "background_width": 0.14, "background_height": 0.14,
        "background_vertical_offset": 0.0, "background_horizontal_offset": 0.0,
        "background_fill": "", "single_char_bg_enable": False,
        "single_char_bg_color": "", "single_char_bg_alpha": 1.0,
        "single_char_bg_round_radius": 0.3,
        "single_char_bg_width": 0.0, "single_char_bg_height": 0.0,
        "single_char_bg_vertical_offset": 0.0,
        "single_char_bg_horizontal_offset": 0.0,
        "font_team_id": "", "tts_auto_update": False,
        "text_preset_resource_id": "", "group_id": group_id,
        "preset_id": "", "preset_name": "", "preset_category": "",
        "preset_category_id": "", "preset_index": 0,
        "preset_has_set_alignment": False, "force_apply_line_max_width": False,
        "language": "", "relevance_segment": [], "original_size": [],
        "fixed_width": -1.0, "fixed_height": -1.0, "line_max_width": 0.82,
        "oneline_cutoff": False, "cutoff_postfix": "",
        "subtitle_template_original_fontsize": 0.0, "subtitle_keywords": None,
        "inner_padding": -1.0, "multi_language_current": "none",
        "source_from": "", "is_lyric_effect": False, "lyric_group_id": "",
        "lyrics_template": {"resource_id": "", "resource_name": "", "panel": "",
                            "effect_id": "", "path": "", "category_id": "",
                            "category_name": "", "request_id": ""},
        "is_batch_replace": False, "is_words_linear": False, "ssml_content": "",
        "subtitle_keywords_config": None, "sub_template_id": -1,
        "translate_original_text": "",
    }


def make_animation(anim_id: str) -> dict:
    return {"id": anim_id, "type": "sticker_animation",
            "animations": [], "multi_language_current": "none"}


def make_segment(seg_id: str, text_id: str, anim_id: str,
                 start_us: int, duration_us: int, render_index: int) -> dict:
    """자막 segment. v1 대비 변경:
    - track_render_index: 1 → 2 (★ ch01 정상 기준)
    """
    return {
        "id": seg_id, "source_timerange": None,
        "target_timerange": {"start": start_us, "duration": duration_us},
        "render_timerange": {"start": 0, "duration": 0},
        "desc": "", "state": 0, "speed": 1.0,
        "is_loop": False, "is_tone_modify": False, "reverse": False,
        "intensifies_audio": False, "cartoon": False,
        "volume": 1.0, "last_nonzero_volume": 1.0,
        "clip": {"scale": {"x": 1.0, "y": 1.0}, "rotation": 0.0,
                 "transform": {"x": 0.0, "y": -0.8},
                 "flip": {"vertical": False, "horizontal": False},
                 "alpha": 1.0},
        "uniform_scale": {"on": True, "value": 1.0},
        "material_id": text_id, "extra_material_refs": [anim_id],
        "render_index": render_index, "keyframe_refs": [],
        "enable_lut": False, "enable_adjust": False, "enable_hsl": False,
        "visible": True, "group_id": "",
        "enable_color_curves": True, "enable_hsl_curves": True,
        "track_render_index": 2,             # ★ v1=1 → v2=2
        "hdr_settings": None, "enable_color_wheels": True,
        "track_attribute": 0, "is_placeholder": False, "template_id": "",
        "enable_smart_color_adjust": False, "template_scene": "default",
        "common_keyframes": [], "caption_info": None,
        "responsive_layout": {"enable": False, "target_follow": "",
                              "size_layout": 0, "horizontal_pos_layout": 0,
                              "vertical_pos_layout": 0},
        "enable_color_match_adjust": False, "enable_color_correct_adjust": False,
        "enable_adjust_mask": False, "raw_segment_id": "",
        "lyric_keyframes": None, "enable_video_mask": True,
        "digital_human_template_group_id": "", "color_correct_alg_result": "",
        "source": "segmentsourcenormal",
        "enable_mask_stroke": False, "enable_mask_shadow": False,
        "enable_color_adjust_pro": False,
    }


# ─── 메인 주입 ─────────────────────────────────────────
def inject(draft_dir: Path, srt_path: Path,
           font_path: str = DEFAULT_FONT_PATH) -> int:
    """draft_dir 의 draft_content.json + draft_meta_info.json 에 자막 주입.

    1. SRT 를 Resources/ 에 복사
    2. draft_content.json:
       - materials.texts 에 자막 material 들 추가
       - materials.material_animations 에 animation 들 추가
       - tracks 에 type=text 트랙 추가 (segments 포함)
    3. draft_meta_info.json:
       - draft_materials[type=2] 버킷에 SRT 엔트리 등록 (있으면 추가, 없으면 신설)

    재실행 안전: 기존 자막 트랙·텍스트 자료 제거 후 재생성.
    """
    content_path = draft_dir / "draft_content.json"
    meta_path = draft_dir / "draft_meta_info.json"
    if not content_path.is_file() or not meta_path.is_file():
        raise FileNotFoundError(
            f"draft_content.json / draft_meta_info.json 없음: {draft_dir}")

    # 백업
    shutil.copy2(content_path, content_path.with_suffix(".json.bak_before_subs"))
    shutil.copy2(meta_path, meta_path.with_suffix(".json.bak_before_subs"))

    # SRT → Resources/ 복사
    res_dir = draft_dir / "Resources"
    res_dir.mkdir(exist_ok=True)
    srt_target = res_dir / srt_path.name
    if srt_path.resolve() != srt_target.resolve():
        shutil.copy2(srt_path, srt_target)

    # 파싱
    cues = parse_srt(srt_target)
    print(f"[info] SRT cues parsed: {len(cues)}")
    if not cues:
        print("[warn] cue 없음 — 빈 SRT 거나 파싱 실패")
        return 0

    # draft_content.json 수정
    with content_path.open(encoding="utf-8") as f:
        content = json.load(f)

    # 기존 text 트랙 제거 (재실행 안전성)
    content["tracks"] = [t for t in content["tracks"] if t.get("type") != "text"]
    content["materials"].setdefault("texts", [])
    content["materials"]["texts"] = [
        t for t in content["materials"]["texts"]
        if t.get("type") != "subtitle"]
    content["materials"].setdefault("material_animations", [])

    group_id = f"sceneweaver_subs_v2_{int(cues[0]['start_us'])}"
    text_track_id = gen_uuid()
    segments = []
    for i, cue in enumerate(cues):
        text_id = gen_uuid()
        anim_id = gen_uuid()
        seg_id = gen_uuid()
        content["materials"]["texts"].append(
            make_text_material(text_id, cue["text"], group_id, font_path))
        content["materials"]["material_animations"].append(
            make_animation(anim_id))
        segments.append(make_segment(seg_id, text_id, anim_id,
                                     cue["start_us"], cue["duration_us"],
                                     14000 + i))

    content["tracks"].append({
        "id": text_track_id, "type": "text", "segments": segments,
        "flag": 1, "attribute": 0, "name": "", "is_default_name": True,
    })

    with content_path.open("w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, separators=(",", ":"))

    # draft_meta_info.json — type=2 (자막) 버킷에 SRT 엔트리 등록
    with meta_path.open(encoding="utf-8") as f:
        meta = json.load(f)
    srt_name = srt_target.name
    fold_path = meta.get("draft_fold_path", str(draft_dir).replace("\\", "/"))
    srt_entry = {
        "ai_group_type": "", "create_time": 0, "duration": 0, "enter_from": 0,
        "extra_info": srt_name,
        "file_Path": f"{fold_path}/Resources/{srt_name}",
        "height": 0, "id": str(uuid.uuid4()),
        "import_time": 0, "import_time_ms": 0, "item_source": 1,
        "md5": "", "metetype": "none",
        "roughcut_time_range": {"duration": 0, "start": -1},
        "sub_time_range": {"duration": -1, "start": -1},
        "type": 0, "width": 0,
    }
    buckets = {b["type"]: b for b in meta.get("draft_materials", [])}
    if 2 not in buckets:
        meta.setdefault("draft_materials", []).append({"type": 2, "value": []})
        buckets = {b["type"]: b for b in meta["draft_materials"]}
    bucket2 = buckets[2]
    bucket2["value"] = [v for v in bucket2.get("value", [])
                       if v.get("extra_info") != srt_name]
    bucket2["value"].append(srt_entry)

    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, separators=(",", ":"))

    return len(cues)


# ─── 엔트리포인트 ──────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(
        description="CapCut 8.x 드래프트에 자막 트랙 자동 주입 (v2, ch01 정상 동작 기준)")
    parser.add_argument("chapter", nargs="?", default=None,
                        help="챕터 번호 (예: 02). --draft / --srt 사용 시 생략")
    parser.add_argument("--workspace", default=None,
                        help="workspace 루트 (default: ./workspace)")
    parser.add_argument("--draft", default=None,
                        help="드래프트 폴더 직접 지정 (chapter 모드 무시)")
    parser.add_argument("--srt", default=None,
                        help="SRT 파일 직접 지정 (chapter 모드 무시)")
    parser.add_argument("--font", default=DEFAULT_FONT_PATH,
                        help="폰트 경로 (default: malgun.ttf)")
    args = parser.parse_args()

    if args.draft and args.srt:
        draft_dir = Path(args.draft)
        srt_path = Path(args.srt)
    elif args.chapter:
        chapter = args.chapter.zfill(2)
        ws_root = (Path(args.workspace) if args.workspace
                   else Path.cwd() / "workspace")
        workspace = ws_root / f"ch{chapter}"
        draft_dir = workspace / "draft"
        # SRT 자동 탐지
        candidates = list((workspace / "subtitles").glob("*.srt")) if \
            (workspace / "subtitles").is_dir() else []
        if not candidates:
            print(f"[error] subtitles/*.srt 없음: {workspace / 'subtitles'}",
                  file=sys.stderr)
            return 1
        srt_path = candidates[0]
        if len(candidates) > 1:
            print(f"[warn] SRT 여러 개. 첫 번째 사용: {srt_path}")
    else:
        parser.error("chapter 또는 --draft + --srt 중 하나는 필수")

    if not draft_dir.is_dir():
        print(f"[error] draft 폴더 없음: {draft_dir}", file=sys.stderr)
        return 1
    if not srt_path.is_file():
        print(f"[error] SRT 없음: {srt_path}", file=sys.stderr)
        return 1

    try:
        n = inject(draft_dir, srt_path, args.font)
    except (FileNotFoundError, ValueError) as e:
        print(f"[error] {e}", file=sys.stderr)
        return 1

    print(f"\n[ok] 자막 {n}개 주입 완료: {draft_dir}")
    print(f"     SRT: {srt_path.name}")
    print(f"     폰트: {args.font}")
    print(f"\n다음 단계:")
    print(f"  python install_draft.py {args.chapter or '<N>'}   # CapCut 에 설치 (재실행)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
