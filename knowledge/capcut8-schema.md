# CapCut 8.x 드래프트 폴더 스키마 (진행 중)

> **상태**: 샘플 확보됨 (2026-04-21). 실제 필드 파싱·매핑은 이후 세션에서 진행.
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
