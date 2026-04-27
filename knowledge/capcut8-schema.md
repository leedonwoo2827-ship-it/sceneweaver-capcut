# CapCut 8.x 드래프트 폴더 스키마

> **상태 (2026-04-27, v0.2.0)**: 풀 자동 빌드·설치·자막 주입 검증 완료. ch02 (이미지 23 + 오디오 23 + 자막 200 cue) 자동 생성 → CapCut 8.5.0 정상 로드 + 자막 트랙 정상 배치 확인. v0.1 시절 "비정상적인 경로" 3종 원인, `root_meta_info.json` 전역 레지스트리, 자막 트랙 형식 5필드 fix 모두 확보·자동화. **미완**: `transition_hint`/`mood`/`era` → 효과 `effect_id` 매핑 (v0.3, 추가 샘플 필요).
>
> **샘플 위치**: [`_assetst/0421/`](../_assetst/0421/) — CapCut 8.5.0에서 최소 자산(이미지 1장 + 오디오 1개 + 자막 SRT 1개)을 드래그한 뒤 저장한 실제 드래프트 폴더 사본.

## 샘플에서 관찰된 폴더 구조

```
_assetst/0421/               ← CapCut 8.5.0 실제 드래프트 폴더
├── draft_content.json       ★ v8.x 타임라인 본체 (v4.x의 draft_info.json 역할)
├── draft_content.json.bak   백업 사본 (CapCut 자동 생성)
├── draft_meta_info.json     드래프트 메타 (ID, 이름, 썸네일, 생성시각)
├── draft_agency_config.json
├── draft_biz_config.json
├── draft_virtual_store.json
├── draft_cover.jpg          드래프트 썸네일 이미지
├── draft_settings           (확장자 없는 설정 파일)
├── attachment_editing.json
├── key_value.json
├── performance_opt_info.json
├── timeline_layout.json
├── template.tmp             (바이너리 템플릿 캐시?)
├── template-2.tmp
├── Resources/               ★ 이미지·오디오·자막 재료 (v4.x의 materials/ 역할)
├── adjust_mask/
├── common_attachment/
├── matting/
├── qr_upload/
├── smart_crop/
└── subdraft/
```

## v4.x → v8.x 주요 변경 (v0.2 빌더 실패의 근본 원인)

| v4.x 가정 (구 SceneWeaver) | v8.x 실제 | 비고 |
|---|---|---|
| `draft_info.json` | **`draft_content.json`** | 이름 자체가 바뀜. v0.2는 draft_info.json만 만들어 CapCut 8.x가 인식 못함 |
| `materials/` | **`Resources/`** | 재료 폴더 이름도 변경 |
| (없음) | `draft_agency_config.json`, `draft_biz_config.json`, `draft_virtual_store.json` 등 10+ 파일 | v8.x 필수 부속 파일들. 없으면 로드 실패 가능성 |
| (없음) | `draft_cover.jpg` | 드래프트 썸네일 이미지 파일. 프로젝트 목록 표시용 |
| (없음) | `adjust_mask/`, `matting/`, `smart_crop/` 등 하위 폴더 | 편집 기능별 캐시. 비어있어도 폴더 자체는 존재 |

## 2026-04-21 검증 결과 ★ ch01 실빌드 성공

v0.1 스텁 상태에서 "샘플 기반 수동 조립" 지시로 Claude가 ch01 드래프트를 어셈블 → CapCut 8.5.0에서 **정상 로드 확인**. 폴더명 `ch01_draft_20260421`, 씬 20 + 오디오 20 타임라인 정상 배치, 길이 8:01.

### 추가 발견 (반드시 v0.2 빌더에 반영)

**`%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\root_meta_info.json`** 이라는 **CapCut 전역 드래프트 레지스트리** 파일이 루트에 존재한다. 이 파일의 `all_draft_store` 배열에 신규 드래프트 엔트리를 추가해야 **CapCut 프로젝트 목록에 표시**된다. 드래프트 폴더만 복사하고 `root_meta_info.json` 을 건드리지 않으면 CapCut은 인식하지 못함 — v0.2.x 시절 빌더 실패의 또다른 원인.

v0.2 빌더가 해야 할 일:
1. `root_meta_info.json` 읽기 → 백업 생성 (`.bak_before_{chapter}`)
2. `all_draft_store` 에 새 드래프트 엔트리 추가 (UUID, 폴더명, 썸네일, 생성시각 등)
3. 저장 → CapCut 재시작 후 목록에 표시됨

### 미완 (v0.2에서 다룰 것)

- 자막 자동 import: 현재는 CapCut UI에서 `Import → Subtitle` 로 `Resources/ch01_*.srt` 21개를 수동 불러와야 함. 타임라인 자막 트랙에 자동 삽입되는 구조는 `draft_content.json` 의 추가 분석 필요.

---

## 2026-04-21 초기 관찰 (draft_meta_info.json 만 분석)

샘플의 `draft_meta_info.json` 에서 **"비정상적인 경로" 에러의 유력 원인** 3가지가 드러났다:

### 1. 절대경로 하드코딩 ★ 최유력 원인

```json
{
  "draft_fold_path": "C:/Users/leedonwoo/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/0421",
  "draft_root_path": "C:\\Users\\leedonwoo\\AppData\\Local\\CapCut\\User Data\\Projects\\com.lveditor.draft"
}
```

드래프트 폴더의 **전체 절대경로**가 메타에 박혀있다. 폴더를 다른 위치로 복사하면 `draft_fold_path` 와 실제 위치가 불일치 → CapCut이 "비정상적인 경로"로 판정.

**빌더가 해야 할 일**: 드래프트를 최종 설치 위치(`%LOCALAPPDATA%\CapCut\...\{폴더명}`)로 복사한 뒤 `draft_fold_path` / `draft_root_path` 를 그 위치에 맞게 **덮어쓴다**. 또는 빌드 단계에서 아예 해당 경로로 직접 생성.

### 2. 소스 파일 경로도 절대경로

```json
{
  "draft_materials": [{
    "type": 0,
    "value": [
      {
        "extra_info": "ch01_01_opening_title_1.jpeg",
        "file_Path": "D:/cl150y/ch01/images/ch01_01_opening_title_1.jpeg",
        "metetype": "photo",
        ...
      },
      {
        "extra_info": "01.wav",
        "file_Path": "D:/cl150y/ch01/audio/01.wav",
        "metetype": "music",
        ...
      }
    ]
  }]
}
```

재료 파일도 외부 절대경로로 참조. **원본 소스가 없어지면 CapCut에서 "미디어 없음"** 표시.

**빌더가 해야 할 일**: 재료를 `Resources/` 안에 복사한 뒤 `file_Path` 를 `Resources/{파일명}` 같은 상대경로로 바꾸거나, 또는 절대경로를 설치 후 위치 기준으로 재작성.

### 3. draft_id vs 폴더명

샘플:
- 폴더명: `0421` (사용자가 CapCut UI에서 정한 프로젝트 이름)
- `draft_id`: `"856E55A1-5256-477d-81D1-4F3F6136026E"` (UUID, 대문자 혼합)
- `draft_name`: `"0421"` (폴더명과 동일)

**예상과 달리 폴더명은 UUID와 매칭할 필요 없음**. 오히려 `draft_name` 과 폴더명이 같다. UUID는 내부 식별자로만 쓰이는 듯.

**빌더가 해야 할 일**: 폴더명을 `ch{NN}_draft_{YYYYMMDD}` 같은 사람 친화적 이름으로 정하고, `draft_name` 을 같은 값으로 박음. `draft_id` 는 새 UUID 생성.

### 4. 기타 관찰

- 시간 단위: 마이크로초 μs 유지 (v4.x와 동일). 예: `"duration": 33333` (작은 값은 ms 단위인 듯, 다시 확인 필요)
- `draft_materials` 구조: `type` 별(0=이미지/오디오, 1~8=?)로 나뉜 배열. 추가 분석 필요.
- `tm_draft_create`, `tm_draft_modified` 등 타임스탬프는 Unix epoch ms × 10^3 형식

### 아직 분석 안 된 것

- **`draft_content.json`** 전체 구조 (13.7 KB — 타임라인 본체)
- 트랙 구조 (비디오·오디오·자막)
- 전환·필터의 `effect_id` 실제 값
- 부속 파일 (`draft_agency_config.json`, `draft_biz_config.json` 등) 의 최소 필수 내용

## 분석 계획 (다음 세션)

### 1순위 — 필수 식별 (드래프트가 CapCut에서 열리기 위한 최소 조건)

- [ ] `draft_meta_info.json` 의 `id` / `draft_id` 필드 구조 파악
- [ ] 폴더명과 메타 ID의 매칭 규칙 확인 (UUID 일치 강제?)
- [ ] `draft_content.json` 최상위 필드 목록 (`tracks`, `materials`, `canvas_config`, `duration` 등이 어떤 이름으로 있는지)
- [ ] `Resources/` 참조 방식: 절대경로? 상대경로? 토큰?

### 2순위 — 트랙·재료 매핑

- [ ] 비디오(이미지) 트랙이 `draft_content.json` 어디에, 어떤 구조로 표현되는가
- [ ] 오디오 트랙(wav)의 참조 방식
- [ ] 자막 트랙: SRT를 그대로 참조? 아니면 CapCut 내부 포맷(ASS/내부 JSON)으로 변환?
- [ ] 시간 단위 (v4.x는 마이크로초 μs, v8.x도 같은지)

### 3순위 — scene_meta 매핑

- [ ] `transition_hint` → CapCut 8.x 전환 `effect_id` 문자열
- [ ] `mood` / `era` → 필터·컬러 그레이딩 `preset_id`
- [ ] `subtitle` / `text_overlay` → 텍스트 트랙 스타일

### 4순위 — 부속 파일

- [ ] `draft_agency_config.json` 역할 (계정/에이전시 설정?)
- [ ] `draft_biz_config.json` (비즈 계정 관련?)
- [ ] `draft_virtual_store.json` (가상 저장소?)
- [ ] `performance_opt_info.json` (성능 최적화 힌트?)
- [ ] `timeline_layout.json` (UI 레이아웃 — 빌드 시 무시해도 될 가능성)
- [ ] `attachment_editing.json`, `key_value.json`, `draft_settings` — 실험으로 최소 필수 파일 판별

## 작업 방식

1. `_assetst/0421/draft_content.json` 먼저 열어 구조 덤프
2. `draft_meta_info.json` 에서 ID 필드 위치 파악
3. **최소 필수 파일 세트** 가설 수립 (예: draft_content + draft_meta_info + Resources/ + draft_cover.jpg) 후 다른 파일 제거해 CapCut 로드 시도
4. ch01 자산으로 동일 구조 생성하는 빌더 작성
5. 빌드 → 설치 → CapCut에서 열기 → 실패 시 diff 기반 교정 루프

## 샘플 추가 요청 (필요시)

현재 샘플은 "이미지 1 + 오디오 1 + 자막 1" 최소 케이스. 더 복잡한 매핑(전환·컬러 필터·mood) 파악을 위해 다음이 필요할 수 있음:

- 샘플 B: 씬 2개 + 중간에 전환 효과(예: 디졸브) 적용
- 샘플 C: 씬 1개 + mood/era 필터(세피아 등) 적용
- 샘플 D: 자막 스타일(폰트·크기·위치) 변경된 상태

필요하면 다음 세션 시작 시 요청.

---

## 2026-04-27 v0.2 검증으로 추가 확보된 정보

v0.1 분석 (위) 이후 풀 자동화 (build_draft.py + install_draft.py + inject_subtitles_v2.py) 작성·검증 과정에서 정확히 확인된 추가 사항. 이 PC 의 ch01_draft_20260421 (자막 정상 동작) 과 사용자 PC 의 ch02_draft_20260427 (자막 깨짐) 진단 데이터 기반.

### 자료 참조 패턴 (segment.extra_material_refs)

`draft_content.json` 의 segment 가 어떤 자료 카테고리를 참조하는지:

| segment 타입 | extra_material_refs 개수 | 참조 카테고리 |
|---|---|---|
| video | **7** | speeds, placeholder_infos, canvases, sound_channel_mappings, material_colors, loudnesses, vocal_separations |
| audio | **5** | speeds, placeholder_infos, beats, sound_channel_mappings, vocal_separations |
| text (자막) | **1** | material_animations |

### 자료 카운트 패턴 (N개 이미지 + N개 오디오 + M개 자막)

| 카테고리 | 개수 |
|---|---|
| videos, audios, canvases, material_colors, loudnesses, beats | N |
| placeholder_infos, sound_channel_mappings, speeds, vocal_separations | **2N** (video + audio segment 별 1개씩) |
| material_animations, texts | M (자막 cue 수) |

### 자막 트랙 형식 — v1 깨짐 vs v2 정상 (deep diff 결과)

`inject_subtitles.py` (v1) 이 CapCut 8.5.0 에서 거부된 직접 원인. ch01 정상 동작 샘플과 v1 출력 비교 결과 정확히 5개 필드 값만 다름. 키 누락/잉여 0:

| 위치 | 필드 | v1 (깨짐) | v2 (정상) |
|---|---|---|---|
| `materials.texts[]` | `check_flag` | 7 | **23** |
| `materials.texts[]` | `background_alpha` | 1.0 | **0.5** |
| `materials.texts[]` | `background_color` | "" | **"#000000"** |
| `materials.texts[]` | `background_style` | 0 | **1** |
| `tracks[type=text].segments[]` | `track_render_index` | 1 | **2** |

자막 트랙 자체의 `flag=1, attribute=0` 은 v1/v2 동일 (문제 아님).

자막 segment 의 다른 핵심 필드:
- `clip.transform`: `{"x": 0.0, "y": -0.8}` (화면 하단 위치)
- `material_id`: 텍스트 자료 UUID
- `extra_material_refs`: animation 자료 UUID 1개
- `render_index`: 14000 + 인덱스 (자막 segment 별 14000부터 순차)

### `root_meta_info.json` 전역 레지스트리 — 정확한 필드 셋

새 드래프트가 CapCut 목록에 뜨려면 `all_draft_store[]` 에 추가해야 할 엔트리 (~30개 필드):

**핵심 (반드시 정확해야 함):**
- `draft_id` — `draft_meta_info.json` 의 `draft_id` 와 일치
- `draft_fold_path` — 실제 설치 위치 (`%LOCALAPPDATA%\CapCut\...\<폴더명>`)
- `draft_root_path` — 부모 (`%LOCALAPPDATA%\CapCut\...\com.lveditor.draft`)
- `draft_name` — 폴더명 (`ch{NN}_draft_{YYYYMMDD}` 권장)
- `draft_json_file` — `<draft_fold_path>\draft_content.json`
- `draft_cover` — `<draft_fold_path>\draft_cover.jpg`

**카운터 / 시각:**
- `draft_timeline_materials_size` — Resources/ 합계 bytes
- `tm_draft_create`, `tm_draft_modified` — Unix epoch microseconds (16자리 정수)
- `tm_duration` — 영상 길이 microseconds

**default 값 (~25개):**
- `cloud_draft_*: false`, `draft_cloud_*: ""`/0/-1
- `draft_is_*: false` (~7개 boolean flag)
- `streaming_edit_draft_ready: true`
- `tm_draft_cloud_*: -1 / 0 / ""`
- `tm_draft_removed: 0`, `draft_type: ""`

또한 root 레벨에 `draft_ids` += 1 갱신 필요.

### 경로 필드 갱신 (`install_draft.py` 가 자동 처리)

빌더가 만든 드래프트 폴더를 CapCut 디렉터리로 복사한 후, 다음 path 필드들을 실제 설치 위치 기준으로 재작성해야 함 (안 그러면 "비정상적인 경로" 또는 "미디어 없음"):

- `draft_meta_info.json`
  - `draft_fold_path` / `draft_root_path`
  - `draft_materials[].value[].file_Path` (이미지/오디오/SRT 모두)
- `draft_content.json`
  - `materials.videos[].path`
  - `materials.audios[].path`

`install_draft.py` 가 이를 자동 처리. 수동 폴더 복사 시에는 직접 갱신 필수.

### UUID 형식

CapCut 은 표준 36자리 UUID (8-4-4-4-12) 를 사용. 4번째 그룹만 소문자, 나머지는 대문자:

```
606E1F6B-7013-4B48-8f7e-644D865E3EA9
                    ↑↑↑↑ 소문자
```

`build_draft.py::gen_uuid()` 가 이 형식으로 생성. 표준 외 형식 (하이픈 누락, 길이 변형) 은 CapCut 이 거부할 가능성 있음.

### 부속 파일 — 최소 필수 세트 (검증됨)

`build_draft.py` 가 생성하고 ch02 검증으로 동작 확인된 부속 파일들 (`templates/` 에 보존):

- `attachment_editing.json` — default 값 객체 (1.7KB, 정적)
- `draft_agency_config.json` — `video_resolution: 720` 등 (154 bytes, 정적)
- `draft_biz_config.json` — 빈 파일 (0 bytes)
- `draft_settings` — INI 형식, `draft_create_time` / `draft_last_edit_time` 동적
- `draft_virtual_store.json` — 0421 그대로 복사 (UUID 매칭 안 해도 동작)
- `key_value.json` — 0421 그대로 (3.2KB, 자료 메타. 매칭 안 해도 default 처리됨)
- `performance_opt_info.json` — 거의 빈 파일 (71 bytes)
- `timeline_layout.json` — `timelineIds` 동적

빈 폴더 7개 (`adjust_mask`, `common_attachment`, `matting`, `qr_upload`, `smart_crop`, `subdraft`, `Resources`) 도 반드시 존재해야 함.

CapCut 이 자동 생성하는 것 (빌더가 만들 필요 없음):
- `draft_content.json.bak` (자동 백업)
- `template.tmp`, `template-2.tmp` (캐시)
- `draft.extra` (CapCut 메타)

### 회귀 보호 (재발 방지)

자막 트랙이 다시 깨지거나 빌더가 거부되지 않게:

1. **정상 동작 샘플 보존**: `_assetst/0421/` (자막 없는 정상) + 이 PC 의 `ch01_draft_20260421` (자막 정상). git 에는 0421 만 (저작권). ch01 은 PC 에 보존.
2. **회귀 검증**: 새 빌드 후 ch01 의 `draft_content.json` 과 키 셋 / 자료 카운트 패턴 / 자료 ref 개수 비교
3. **새 CapCut 버전 대응**: 형식 깨질 시 정상 동작 새 샘플 확보 후 deep-diff 부터. 추측으로 수정 금지 (v1 사고 교훈).
