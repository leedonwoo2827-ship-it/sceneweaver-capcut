---
description: 수집된 자산과 편집된 SRT를 조합하여 CapCut 8.x 데스크톱이 직접 열 수 있는 드래프트 폴더를 생성한다.
argument-hint: "[챕터 번호] [--install] [--uuid <UUID>]"
---

# /weave-draft

`workspace/ch{NN}/` 의 자산을 CapCut 8.x 드래프트 폴더로 조립한다.

> **⚠ v0.1 스텁** — CapCut 8.x 스키마 샘플 분석 진행 중. 실체 빌드는 다음 세션에서 구현. 현재는 인터페이스 명세와 뼈대만 정의되어 있다.

## 사전 조건

- `/weave-ingest` 완료 — script.json + images + audio
- `/weave-subtitle` 완료 + **사람의 SRT 편집 완료**
- CapCut 8.5.0+ 데스크톱 설치

## 실행 흐름 (예정)

### Step 1: 검증
씬 수 vs 이미지·오디오·SRT 수 일치 확인. 불일치 시 중단.

### Step 2: 드래프트 UUID·폴더명 결정
- UUID 생성 (사용자가 `--uuid` 명시하면 그 값 사용)
- 폴더명: 샘플 분석 결과에 따라 확정 (UUID 그대로 또는 `ch{NN}_draft_{YYYYMMDD}_{UUID}` 형태)

### Step 3: draft_content.json 빌드
v8.x 메인 본체. 씬 이미지·오디오·자막 트랙을 조립. 시간 단위·필드 구조는 [knowledge/capcut8-schema.md](../knowledge/capcut8-schema.md) 에 따라 확정 예정.

### Step 4: draft_meta_info.json 빌드
드래프트 ID·이름·썸네일(`draft_cover.jpg` 자동 생성)·생성 시각.

### Step 5: 부속 파일 생성
v8.x 가 요구하는 최소 부속 파일 세트(`draft_agency_config.json`, `draft_biz_config.json`, `draft_virtual_store.json`, 기타). 샘플에서 관찰한 최소 필수 파일만 생성.

### Step 6: Resources/ 구성
이미지·오디오·자막 사본을 `Resources/` 하위에 배치. 이름 규칙은 샘플 관찰 후 확정.

### Step 7: 설치 안내 또는 자동 설치
- 기본: 드래프트 폴더 경로만 안내
- `--install` 옵션: `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\` 로 직접 복사

## 옵션

| 옵션 | 동작 |
|---|---|
| `--install` | CapCut 드래프트 디렉터리로 자동 복사 (Cowork 샌드박스에서는 robocopy 스크립트 생성) |
| `--uuid {UUID}` | 드래프트 ID 수동 지정 |

## 산출물 (예정)

```
workspace/ch{NN}/draft/
├── draft_content.json
├── draft_meta_info.json
├── draft_cover.jpg
├── (v8.x 필수 부속 파일들)
└── Resources/
    ├── ch{NN}_{SS}_image.{jpeg,png}
    ├── ch{NN}_{SS}_narration.{wav,mp3}
    └── ch{NN}_{SS}.srt
```

## 구현 로드맵

1. [knowledge/capcut8-schema.md](../knowledge/capcut8-schema.md) 의 "1~4순위" 항목 분석 완료
2. [skills/build-capcut-draft/SKILL.md](../skills/build-capcut-draft/SKILL.md) 실체 구현
3. ch01 빌드 → CapCut 8.5.0 에서 열기 검증
4. 에러 시 필드별 이진 탐색 교정 루프
