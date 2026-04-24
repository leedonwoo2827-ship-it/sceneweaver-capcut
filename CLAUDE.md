# SceneWeaver-CapCut — CapCut 8.x 드래프트 빌더

## 프로젝트 개요

ScriptForge의 마스터 대본과 FlowGenie 이미지, TTS 내레이션을 한 챕터 단위로 모아, **CapCut 8.x 데스크톱이 직접 열 수 있는 드래프트 폴더**를 생성하는 Claude Code 스킬 세트. 드래프트 빌드 전에 **사람이 자막을 손보는 단계**를 명시적으로 끼워넣어, 자동화와 편집 자유도를 동시에 확보한다.

> **자매 레포**: [sceneweaver](https://github.com/leedonwoo2827-ship-it/sceneweaver) — 같은 상류(ScriptForge/FlowGenie/TTS) 자산을 받아 **FFmpeg로 mp4를 직접 렌더**하는 버전. 하류를 NLE가 아닌 완성 영상으로 받으려면 그쪽을 쓴다.

## 파이프라인 위치

```
StoryLens → ScriptForge → FlowGenie + TTS → [SceneWeaver-CapCut]
(상담/기획)  (대본 생성)   (이미지+음성)      (CapCut 드래프트)
```

- **상류**:
  - ScriptForge: `ch{NN}_script.json` (마스터 대본)
  - FlowGenie: `ch{NN}_{SS}_*.{png,jpg,jpeg}` (씬별 이미지)
  - TTS: `ch{NN}_{SS}_narration.{mp3,wav}` (씬별 내레이션)
- **하류**: CapCut 8.5.0+ 데스크톱. 사용자가 드래프트 폴더를 열어 최종 편집·렌더.

## 핵심 규칙

1. **입력 JSON 스키마**: ScriptForge 마스터 대본 v1.0을 그대로 받는다. 스키마 변경 시 ScriptForge `CLAUDE.md`를 먼저 업데이트.
2. **챕터별 단일 워크스페이스**: `workspace/ch{NN}/` 하나에 해당 챕터 자산과 드래프트가 모인다.
3. **자막 편집 개입 포인트**: `/weave-subtitle` 이후 `/weave-draft` 이전에 **사람이 SRT를 수정한다**. 자동으로 넘어가지 않는다.
4. **SRT 인코딩**: UTF-8 BOM + CRLF.
5. **자막 길이 제한**: 한 줄 최대 18자(한글 기준), 두 줄까지 허용, 한 큐 최대 36자.
6. **파일명 승계 & 정규화**: 상류 표준 명명(`ch{NN}_{SS}_*`) 승계. 비표준 소스(`.jpeg`/`.wav`/숫자명)는 `workspace/` 복사 시점에 표준으로 정규화. 소스 폴더 원본은 절대 수정 안 함.
7. **단계별 확인**: 전체 `/weave` 실행 시 단계 사이마다 사용자 확인.
8. **CapCut 8.x 스키마 준수**: `draft_content.json`(v4.x의 draft_info.json 역할) + `draft_meta_info.json` + v8.x 부속 파일 세트 + `Resources/`. 4.x 스키마로 만들면 "비정상적인 경로" 에러로 열리지 않는다.
9. **드래프트 UUID ↔ 폴더명 매칭**: v8.x는 드래프트 폴더명과 내부 UUID 매칭을 엄격히 검증. 빌더가 동일 UUID를 생성·매핑해야 한다.
10. **드래프트 폴더는 독립 산출물**: CapCut 드래프트 디렉터리(`%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\`)에 복사하기 전에는 프로젝트 내부에만 존재. 복사는 사용자 수동 또는 `/weave-draft --install`.

## 워크스페이스 구조

```
workspace/ch{NN}/
├── script.json                           # ScriptForge 복사본 (읽기 전용)
├── images/ch{NN}_{SS}_*.{png,jpg,jpeg}
├── audio/ch{NN}_{SS}_narration.{mp3,wav}
├── subtitles/                            # ★ 생성된 SRT — 사람이 수정
│   ├── ch{NN}_{SS}.srt
│   └── ch{NN}_full.srt
└── draft/                                # ★ CapCut 8.x 드래프트
    ├── draft_content.json
    ├── draft_meta_info.json
    ├── draft_cover.jpg
    ├── (v8.x 부속 파일들)
    └── Resources/
        ├── ch{NN}_{SS}_image.{jpeg,png}
        ├── ch{NN}_{SS}_narration.{wav,mp3}
        └── ch{NN}_{SS}.srt
```

## CapCut 8.x 드래프트 스키마

실제 필드 레이아웃은 [knowledge/capcut8-schema.md](knowledge/capcut8-schema.md) 에서 **샘플 기반으로 추가 분석 중**. 샘플 위치: [`_assetst/0421/`](_assetst/0421/) (CapCut 8.5.0 최소 드래프트 실측).

4.x 레거시 참고: [knowledge/capcut-draft-schema.md](knowledge/capcut-draft-schema.md).

## scene_meta → CapCut 매핑 (확정 예정)

| ScriptForge 필드 | 값 예시 | CapCut 반영 (샘플 분석 후 확정) |
|---|---|---|
| `transition_hint` | `fade_in` | 전환 효과 ID (JSON 덤프에서 확인) |
| `mood` | `tension` | 컬러 그레이딩 프리셋 ID |
| `era` | `1950s` | 필터 프리셋 ID (세피아 계열) |
| `bgm_hint` | — | v0.1은 메타만, 실제 BGM 트랙은 후속 |
| `subtitle` | `1953년 11월…` | 상단 자막 오버레이 텍스트 트랙 |

매핑 테이블은 [knowledge/transition-library.md](knowledge/transition-library.md).

## 파일명 규칙

- 이미지: `ch{NN}_{SS}_{영문슬러그}.{png,jpg,jpeg}`
- 오디오: `ch{NN}_{SS}_narration.{mp3,wav}`
- SRT: `ch{NN}_{SS}.srt`, `ch{NN}_full.srt`
- 드래프트 폴더명: 샘플 분석 후 확정 (UUID 포함 규칙 예상)

## 단계 오케스트레이션

1. **`/weave-ingest {N}`** — 상류 자산 → `workspace/ch{N}/` 수집·정규화
2. **`/weave-subtitle {N}`** — `script.json`의 `narration_text` → SRT 생성
3. **(사람 개입)** — `subtitles/` 열어 줄바꿈·타이밍 미세조정
4. **`/weave-draft {N} [--install]`** — CapCut 8.x 드래프트 폴더 빌드 + (옵션) 자동 설치
5. **`/weave {N}`** — 위 세 단계 순차 오케스트레이션

## 시스템 의존성

- **CapCut 8.5.0+** 데스크톱 (Windows/Mac)
- Claude Code 플러그인 설치: `/plugin marketplace add leedonwoo2827-ship-it/sceneweaver-capcut` → `/plugin install sceneweaver-capcut@sceneweaver-capcut`

## 현재 상태 (v0.1.1, 2026-04-21 기준)

- [x] 프로젝트 뼈대 (sceneweaver v0.3에서 분기)
- [x] CapCut 8.x 샘플 JSON 확보 (`_assetst/0421/`)
- [x] `draft_content.json` / `draft_meta_info.json` 기본 필드 분석 ([knowledge/capcut8-schema.md](knowledge/capcut8-schema.md))
- [x] v4.x → v8.x 차이 규명 (`draft_info.json` → `draft_content.json`, `materials/` → `Resources/`, 신규 부속 파일 10+)
- [x] "비정상적인 경로" 에러 원인 3종 규명 (절대경로 하드코딩, 소스 파일 경로, draft_id 규칙)
- [x] `root_meta_info.json` 전역 드래프트 레지스트리 발견 (`all_draft_store` 수정 필수)
- [x] ch01 수동 조립 빌드 → CapCut 8.5.0 정상 로드 (씬 20 + 오디오 20, 8:01)
- [x] 자막 트랙 주입기 ([skills/build-capcut-draft/inject_subtitles.py](skills/build-capcut-draft/inject_subtitles.py))
- [ ] end-to-end 자동 빌더 (`/weave-draft` 스크립트화)
- [ ] `root_meta_info.json` 자동 갱신
- [ ] `transition_hint` / `mood` / `era` 매핑 테이블 확정 (추가 샘플 필요)
