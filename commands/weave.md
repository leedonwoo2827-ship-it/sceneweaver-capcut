---
description: 한 챕터의 자산 수집부터 CapCut 8.x 드래프트 빌드 + 자동 설치까지 전체 플로우. 자막 편집 개입 포인트를 반드시 거친다.
argument-hint: "[챕터 번호] [--script-path <path>] [--images-dir <path>] [--audio-dir <path>] [--no-install]"
---

# /weave

상류 자산 수집 → 자막 SRT 생성 → 사람 편집 → CapCut 드래프트 빌드 + 설치까지의 전체 파이프라인.

## 실행 흐름

### Step 1: 자산 수집 (`/weave-ingest`)

`build-ingest-assets` 스킬 실행:
- ScriptForge `ch{NN}_script.json` → `workspace/ch{NN}/script.json`
- FlowGenie 이미지 → `workspace/ch{NN}/images/`
- TTS 오디오 → `workspace/ch{NN}/audio/`
- 누락 자산 리포트

**사용자 확인**:
- "좋아" → Step 2
- "S번 씬 다시" → 상류로 돌려보내고 대기
- 누락 시 강한 경고

### Step 2: 자막 생성 (`/weave-subtitle`)

`build-subtitles` 스킬 실행:
- `script.json` 의 `narration_text` → 문장 단위 분절 → SRT
- `subtitles/ch{NN}_{SS}.srt` + `subtitles/ch{NN}_full.srt`
- 한 줄 초과·타이밍 초과 큐를 **편집 포인트**로 제시

**사용자 편집 + 확인**:
- 사용자가 에디터에서 SRT 수정
- "수정 끝" / "계속" → Step 3

### Step 3: 드래프트 빌드 + 설치 (`/weave-draft`)

`build-capcut-draft` 스킬 실행:

```bash
python skills/build-capcut-draft/build_draft.py {N}
python skills/build-capcut-draft/inject_subtitles_v2.py {N}
python skills/build-capcut-draft/install_draft.py {N}
```

`--no-install` 플래그면 마지막 단계 스킵 (워크스페이스에 빌드만).

**완료 보고**:
- 워크스페이스 빌드: `workspace/ch{NN}/draft/`
- CapCut 설치: `%LOCALAPPDATA%\CapCut\...\com.lveditor.draft\ch{NN}_draft_{YYYYMMDD}\`
- 사용자에게 안내: CapCut 완전 종료 → 재시작 → 더블클릭

## 진행 원칙

1. **각 단계마다 사용자 확인** — 자동으로 다음 단계로 넘기지 않음
2. **자막 편집 단계는 의무** — Step 2 완료 후 "계속" 없이 Step 3 안 감
3. **되돌아가기** — "자막 다시 뽑아줘" → Step 2 재실행
4. **누락 경고** — 이미지·오디오 수가 script.json 씬 수와 다르면 강한 경고

## 최종 산출물

```
workspace/ch{NN}/
├── script.json
├── images/ch{NN}_{SS}_*.{png,jpg,jpeg}
├── audio/ch{NN}_{SS}_narration.{mp3,wav}
├── subtitles/ch{NN}_{SS}.srt              ← 사람이 수정한 최종본
└── draft/                                  ← CapCut 드래프트 (워크스페이스)
    ├── draft_content.json
    ├── draft_meta_info.json
    ├── draft_cover.jpg
    ├── (부속 파일 8개 + 빈 폴더 7개)
    └── Resources/

%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\ch{NN}_draft_{YYYYMMDD}\   ← 설치 결과 (`--no-install` 없을 때)
```
