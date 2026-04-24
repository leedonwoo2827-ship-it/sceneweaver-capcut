---
name: build-capcut-draft
description: workspace/ch{NN}/의 script.json + images + audio + 편집된 SRT를 CapCut 8.x 데스크톱이 직접 열 수 있는 드래프트 폴더(draft_info.json + draft_meta_info.json + materials/)로 조립한다. scene_meta의 transition_hint/mood/era를 CapCut 내부 효과 ID로 매핑한다. 사용자가 "드래프트 빌드", "CapCut 드래프트", "/weave-draft"라고 하면 이 스킬을 사용한다.
---

# CapCut 8.x 드래프트 빌더 (Build CapCut Draft)

> **상태 (v0.1.1, 2026-04-21 기준)**
> - CapCut 8.5.0 실제 드래프트 샘플 분석 완료 ([_assetst/0421/](../../_assetst/0421/))
> - ch01 수동 조립 빌드 → CapCut 8.5.0 정상 로드 검증 (씬 20 + 오디오 20, 8:01 타임라인)
> - 자막 트랙 주입기 동작: [inject_subtitles.py](./inject_subtitles.py)
> - **미완**: end-to-end 자동 빌더 스크립트, `transition_hint` / `mood` / `era` → CapCut 효과 ID 매핑
>
> 스키마 레퍼런스: [knowledge/capcut8-schema.md](../../knowledge/capcut8-schema.md) (v4.x → v8.x 차이, "비정상적인 경로" 원인, `root_meta_info.json` 전역 레지스트리 포함).

## 사전 조건

- `/weave-ingest` 완료 (`script.json`, `images/`, `audio/` 모두 존재)
- `/weave-subtitle` 완료 + **사람의 SRT 편집 완료** (`subtitles/ch{NN}_*.srt`)
- **CapCut 8.5.0 이상** 데스크톱 설치 (Windows/Mac)
- `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\` 경로 존재

## 처리 단계 (샘플 확보 후 확정)

### 1. 자산 검증
- `script.json` 씬 수 = 이미지 수 = 오디오 수 = SRT 수
- 불일치 시 실행 중단 + 리포트

### 2. 드래프트 UUID·폴더명 결정
CapCut 8.x는 드래프트 폴더명과 `draft_meta_info.json` 내부 드래프트 ID(UUID)가 **일치해야** 한다 (v0.2.x CapCut 4.x 가정으로 만든 빌더가 실패한 주원인 중 하나).

- 폴더명 규칙: `ch{NN}_draft_{YYYYMMDD}_{UUID단축형}` 또는 **UUID 그대로** — 샘플 확인 후 확정
- `draft_meta_info.json` 의 `id` / `draft_id` / `tm_draft_id` 필드에 동일 UUID 박음

### 3. materials/ 구성
`workspace/ch{NN}/draft/materials/` 에 이미지·오디오·SRT **사본** 배치. 이름은 `ch{NN}_{SS}_{image|narration}.{ext}` 유지.

### 4. draft_info.json 빌드
- `canvas_config`: `video_meta.aspect_ratio` → 1920×1080 or 1080×1920
- `duration`: `scenes[].narration_seconds` 합계 × 1_000_000 μs
- `tracks`:
  - 비디오 트랙: 씬 이미지 순차 배치, `transition_hint` → CapCut 전환 효과 ID
  - 오디오 트랙: 내레이션 mp3/wav 순차 배치
  - 자막 트랙: SRT 큐 → CapCut 텍스트 재료
- `materials`: 파일 경로를 **절대경로**로 박지 말고, CapCut이 허용하는 형태로 (샘플 확인 필수)
- `mood`/`era` → 필터 프리셋 ID (샘플 확인 후 매핑)

### 5. draft_meta_info.json 빌드
- `id`: UUID (위 2번과 일치)
- `draft_name`: `ch{NN}_draft_{YYYYMMDD}`
- 생성 시각, 썸네일 후보(첫 이미지) 등
- **CapCut 8.x 필수 필드** (v8에서 새로 생긴 것: 샘플 확인 후 추가)

### 6. 설치 안내 또는 자동 설치
- 기본: 드래프트 폴더 경로만 안내
- `--install` 옵션: `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\` 로 직접 복사
- 복사 대상 폴더명: 위 2번의 UUID 규칙 따름

## 알려진 CapCut 8.x 제약 (v0.2.x 에러로부터 추정)

이전 SceneWeaver(FFmpeg 레포) v0.2.x 가 CapCut 8.5.0 에서 **"비정상적인 경로"** 에러를 냈다. 그 원인으로 추정되는 것들:

1. **드래프트 폴더명과 내부 UUID 불일치** — 8.x는 엄격하게 매칭 검증
2. **절대경로 하드코딩** — `materials/` 참조가 절대경로면 복사 후 경로 안 맞음. 상대경로 또는 CapCut이 재해석하는 토큰 형식 필요
3. **필수 필드 누락** — 4.x 에 없던 새 필드가 8.x에서 필수로 추가됐을 가능성

이 세 가지를 샘플 JSON 비교로 확인하는 것이 다음 세션의 1순위 작업.

## 옵션

| 옵션 | 동작 |
|---|---|
| `--install` | `%LOCALAPPDATA%\CapCut\...com.lveditor.draft\` 로 자동 복사. 기존 동명 드래프트 있으면 덮어쓰기 확인 |
| `--uuid {UUID}` | 드래프트 ID 수동 지정 (기본: 새로 생성) |
| `--no-materials-copy` | materials/ 복사 생략 (외부 경로 참조 — CapCut이 허용하는지 검증 필요) |

## 산출물

```
workspace/ch{NN}/draft/
├── draft_info.json
├── draft_meta_info.json
├── (v8.x 새 파일 — 샘플 확인 후 추가)
└── materials/
    ├── ch{NN}_{SS}_image.{jpeg,png}
    ├── ch{NN}_{SS}_narration.{wav,mp3}
    └── ch{NN}_{SS}.srt
```

## 자막 트랙 주입 (v0.1.1 — 동작함)

[inject_subtitles.py](./inject_subtitles.py) 가 편집된 SRT 를 기존 드래프트에 자막 트랙으로 주입한다. ch01 방식으로 빌드·설치된 드래프트 폴더를 대상으로 실행.

```bash
python skills/build-capcut-draft/inject_subtitles.py \
  "%LOCALAPPDATA%/CapCut/User Data/Projects/com.lveditor.draft/ch01_draft_20260421" \
  "workspace/ch01/subtitles/ch01_full.srt"
```

동작:
- `draft_content.json` 에 text 트랙 + segments 추가, `materials.texts` / `material_animations` 에 항목 등록
- `draft_meta_info.json` 의 `draft_materials[type=2]` (자막 버킷) 에 SRT 엔트리 등록 (없으면 버킷 신설)
- 실행 전 `.json.bak_before_subs` 백업 자동 생성
- 재실행 안전: 기존 subtitle 재료·text 트랙 제거 후 재생성

폰트 기본값 `C:/Windows/Fonts/malgun.ttf`. 다른 폰트는 3번째 인자로 지정.

## TODO (v0.2)

- [x] 2026-04-21 — CapCut 8.5.0 샘플 분석 ([knowledge/capcut8-schema.md](../../knowledge/capcut8-schema.md) 본문)
- [x] 2026-04-21 — UUID·폴더명 규칙 확정 (`draft_name`=폴더명, `draft_id`=신규 UUID)
- [x] 2026-04-21 — ch01 빌드 → CapCut 8.5.0 열기 검증
- [x] 2026-04-21 — 자막 트랙 주입 (`inject_subtitles.py`)
- [ ] end-to-end 자동 빌더 (`script.json` + `Resources/` → `draft_content.json` 전체 조립)
- [ ] `root_meta_info.json` 의 `all_draft_store` 자동 갱신 (현재 수동)
- [ ] `transition_hint` → CapCut 전환 `effect_id` 매핑 테이블
- [ ] `mood` / `era` → 필터·컬러 그레이딩 `preset_id` 매핑
- [ ] 추가 샘플(전환/필터 적용) 확보 후 매핑 확장
