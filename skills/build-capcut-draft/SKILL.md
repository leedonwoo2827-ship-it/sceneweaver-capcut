---
name: build-capcut-draft
description: workspace/ch{NN}/{images, audio, subtitles}을 CapCut 8.x 데스크톱이 더블클릭만 하면 열리는 드래프트 폴더로 자동 변환. build_draft.py + install_draft.py + inject_subtitles_v2.py 세 스크립트가 한 줄 명령으로 빌드·자막 주입·설치까지 끝낸다. 사용자가 "드래프트 빌드", "CapCut 드래프트", "/weave-draft"라고 하면 이 스킬을 사용한다.
---

# CapCut 8.x 드래프트 빌더

> **상태 (v0.2.0, 2026-04-27 기준) — 풀 자동화 검증 완료**
> - `build_draft.py`: workspace 자산 → CapCut 8.x 드래프트 폴더 자동 빌드 ✅
> - `install_draft.py`: `%LOCALAPPDATA%\CapCut\...` 로 설치 + `root_meta_info.json` 자동 갱신 ✅
> - `inject_subtitles_v2.py`: 자막 트랙 자동 주입 (5필드 fix, ch01 정상 형식) ✅
> - **검증**: ch02 (이미지 23 + 오디오 23 + 자막 200) → CapCut 8.5.0 정상 로드, 자막 타임라인 배치 확인 (2026-04-27)
>
> **알려진 미완**: `transition_hint` / `mood` / `era` → CapCut 효과 ID 매핑 (v0.3, 추가 샘플 필요)
>
> 스키마 레퍼런스: [knowledge/capcut8-schema.md](../../knowledge/capcut8-schema.md)

## 한 줄 사용법

```bash
# 1. 빌드 (자막 제외)
python skills/build-capcut-draft/build_draft.py 02

# 2. 자막 주입 (선택)
python skills/build-capcut-draft/inject_subtitles_v2.py 02

# 3. CapCut 으로 설치
python skills/build-capcut-draft/install_draft.py 02
```

→ CapCut 완전 종료 후 재실행 → 프로젝트 목록에서 더블클릭 → 자동 배치된 영상·음성·자막 확인.

## 사전 조건

- **CapCut 8.5.0 이상** 데스크톱 설치 (Windows 우선 지원, Mac 미검증)
- **CapCut 을 한 번이라도 실행하고 프로젝트 저장** (`%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\` 경로와 `root_meta_info.json` 이 생성되어 있어야 함)
- **Python 3.9+**
- **워크스페이스 자산** 준비:
  ```
  workspace/ch{NN}/
  ├── images/             ← *.jpeg / *.jpg / *.png (정렬된 파일명)
  ├── audio/              ← *.wav (이미지와 같은 개수)
  └── subtitles/          ← (선택) *.srt
  ```
  - 이미지·오디오 개수가 일치해야 함. 정렬된 순서로 1:1 페어링
  - 자막은 `ch{NN}_full.srt` 또는 단일 `*.srt` 파일

## 스크립트별 동작

### `build_draft.py`

**입력**: `workspace/ch{NN}/{images,audio}/`
**출력**: `workspace/ch{NN}/draft/` (CapCut 8.x 정상 로드 가능 폴더)

생성:
- `draft_content.json` — 타임라인·자료. 0421/ch01 정상 샘플 형식 그대로
- `draft_meta_info.json` — 메타·자료 인덱스
- `draft_cover.jpg` — 첫 이미지 사본
- `Resources/` — 이미지·오디오 복사
- 부속 파일 8개 (`templates/` 에서 복제, 일부 placeholder 치환)
- 빈 하위 폴더 7개 (`adjust_mask`, `common_attachment`, `matting`, `qr_upload`, `smart_crop`, `subdraft`, `Resources`)

옵션:
- `--workspace PATH` — workspace 루트 (default: `./workspace`)
- `--output PATH` — 출력 폴더 (default: `workspace/ch{NN}/draft`)
- `--name NAME` — 드래프트 표시명 (default: `ch{NN}_draft_{YYYYMMDD}`)
- `--canvas-w INT` / `--canvas-h INT` — 캔버스 크기 (default: 1920×1080)
- `--fps INT` — default: 30

자료 참조 패턴 (ch01 정상 동작 케이스 deep-diff 로 확보):
- video segment.extra_material_refs (7개): speeds + placeholder_infos + canvases + sound_channel_mappings + material_colors + loudnesses + vocal_separations
- audio segment.extra_material_refs (5개): speeds + placeholder_infos + beats + sound_channel_mappings + vocal_separations

### `inject_subtitles_v2.py`

**입력**: `workspace/ch{NN}/draft/` (build_draft.py 출력) + `workspace/ch{NN}/subtitles/*.srt`
**동작**:
- SRT 를 `Resources/` 에 복사
- `draft_content.json` 에 text 트랙 + segments 추가
- `materials.texts[]` 에 자막 material 등록
- `materials.material_animations[]` 에 animation 등록
- `draft_meta_info.json` 의 `draft_materials[type=2]` 에 SRT 등록
- 실행 전 `.json.bak_before_subs` 자동 백업
- 재실행 안전 (기존 자막 트랙 제거 후 재생성)

옵션:
- `chapter` — 자동 탐지 모드 (workspace/ch{N}/subtitles/*.srt 첫 번째 사용)
- `--draft PATH` + `--srt PATH` — 명시 모드
- `--font PATH` — 폰트 경로 (default: `C:/Windows/Fonts/malgun.ttf`)

**v1 (`inject_subtitles.py`) 은 DEPRECATED**. CapCut 8.5.0 거부 5필드 fix 가 v2 에 들어있음:

| 위치 | 필드 | v1 (깨짐) | v2 (정상) |
|---|---|---|---|
| text material | `check_flag` | 7 | **23** |
| text material | `background_alpha` | 1.0 | **0.5** |
| text material | `background_color` | "" | **"#000000"** |
| text material | `background_style` | 0 | **1** |
| segment | `track_render_index` | 1 | **2** |

### `install_draft.py`

**입력**: `workspace/ch{NN}/draft/` (빌드 + 자막 주입 완료)
**동작**:
1. `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\` 존재 확인
2. `<root>\<draft-name>` 으로 폴더 복사
3. `draft_content.json` / `draft_meta_info.json` 의 `file_Path` 등 경로 필드를 실제 설치 위치로 자동 재작성
4. `root_meta_info.json` 백업 → `all_draft_store[]` 에 새 엔트리 append + `draft_ids += 1`

옵션:
- `--workspace PATH`
- `--target-root PATH` — 디버깅용 (default: `%LOCALAPPDATA%\CapCut\...`)
- `--overwrite` — 기존 동명 폴더 덮어쓰기 + 동일 draft_id 엔트리 갱신 (재설치)

## 산출물

```
workspace/ch{NN}/draft/
├── draft_content.json          # 타임라인 본체
├── draft_meta_info.json        # 메타
├── draft_cover.jpg             # 썸네일
├── attachment_editing.json     # 부속 (templates/)
├── draft_agency_config.json    # 부속
├── draft_biz_config.json       # 부속 (빈 파일)
├── draft_settings              # 부속 (시각 placeholder 채워짐)
├── draft_virtual_store.json    # 부속
├── key_value.json              # 부속
├── performance_opt_info.json   # 부속
├── timeline_layout.json        # 부속 (timeline_id placeholder 채워짐)
├── adjust_mask/                # 빈 폴더
├── common_attachment/          # 빈 폴더
├── matting/                    # 빈 폴더
├── qr_upload/                  # 빈 폴더
├── smart_crop/                 # 빈 폴더
├── subdraft/                   # 빈 폴더
└── Resources/
    ├── ch{NN}_{SS}_*.{jpeg,jpg,png}
    ├── *.wav
    └── ch{NN}_full.srt   (자막 주입 시)
```

## 알려진 CapCut 8.x 제약 (해결됨)

이전 v0.1.x 시절 `inject_subtitles.py` 가 만든 자막 트랙이 CapCut 8.5.0 에서 거부된 이슈가 있었음. 2026-04-27 ch01 정상 동작 샘플과 deep-diff 결과 위 5개 필드만 다름이 확인되어 v2 에서 fix.

또한 v0.1.x 시절 빌더 실패 원인 (이전 작업분 참고):
- 드래프트 폴더명과 `draft_id` 매칭 → 해결: `install_draft.py` 가 자동 매칭
- 절대경로 하드코딩 → 해결: `install_draft.py` 가 설치 위치 기준으로 path 재작성
- `root_meta_info.json` 미갱신 → 해결: `install_draft.py` 가 자동 갱신

## TODO (v0.3 이후)

- [ ] `transition_hint` → CapCut 전환 `effect_id` 매핑 테이블 (추가 샘플 필요)
- [ ] `mood` / `era` → 필터·컬러 그레이딩 `preset_id` 매핑
- [ ] BGM 트랙 자동 추가
- [ ] panel-only 자막 모드 (자막을 미디어 패널에만 등록, 트랙 자동 배치는 안 함 — fallback 옵션)
- [ ] Mac 검증

## 회귀 보호

자료 참조 패턴이나 자막 트랙 형식이 다시 깨지지 않도록:
- ch01 정상 동작 샘플의 `draft_content.json` 구조를 회귀 검증 기준으로 유지
- 새 CapCut 버전에서 형식이 바뀌면 0421/ch01 시점의 샘플 보존
- 디버깅 우선순위: 항상 정상 동작 샘플과 deep-diff 부터
