---
description: workspace/ch{NN}/ 의 자산을 CapCut 8.x 드래프트로 빌드 + (선택) 자막 주입 + (선택) 자동 설치까지 한 번에. 한 줄 명령으로 더블클릭만 하면 열리는 드래프트가 생성된다.
argument-hint: "[챕터 번호] [--no-subtitle] [--no-install] [--font <path>] [--canvas-w <int>] [--canvas-h <int>] [--overwrite]"
---

# /weave-draft

`workspace/ch{NN}/` → CapCut 8.x 드래프트 폴더 → CapCut 설치 디렉터리. 기본은 빌드 + 자막 주입 + 설치까지 모두 진행.

## 사전 조건

- `workspace/ch{NN}/images/`, `audio/`, (선택) `subtitles/` 자산 존재
  - 이미지·오디오 개수 일치, 정렬 순서로 1:1 페어링
  - 자막은 `subtitles/*.srt` (UTF-8 BOM 권장)
- CapCut 8.5.0+ 데스크톱 설치 + **한 번이라도 실행해서 프로젝트 저장한 적 있음**
  - `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\` 와 `root_meta_info.json` 이 있어야 설치 단계 통과
- Python 3.9+

## 실행 흐름

### Step 1: 빌드

```bash
python skills/build-capcut-draft/build_draft.py {N} [--canvas-w 1920 --canvas-h 1080]
```

산출물: `workspace/ch{NN}/draft/` (영상·음성만, 자막 제외)

### Step 2: 자막 주입 (기본 ON, `--no-subtitle` 로 끔)

```bash
python skills/build-capcut-draft/inject_subtitles_v2.py {N} [--font <path>]
```

`workspace/ch{NN}/subtitles/*.srt` 자동 탐지. 여러 개면 첫 번째 사용.
SRT 가 없으면 이 단계 자동 스킵.

### Step 3: CapCut 설치 (기본 ON, `--no-install` 로 끔)

```bash
python skills/build-capcut-draft/install_draft.py {N} [--overwrite]
```

`%LOCALAPPDATA%\CapCut\...\com.lveditor.draft\<draft-name>\` 으로 폴더 복사 + path 필드 자동 재작성 + `root_meta_info.json` 의 `all_draft_store[]` 갱신 (백업 자동 생성).

### Step 4: 사용자 안내

```
✅ 빌드 + 자막 주입 + 설치 완료
   드래프트: %LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\ch{NN}_draft_{YYYYMMDD}\

다음 단계:
1. CapCut 완전 종료 (작업관리자에서 CapCut.exe 까지)
2. CapCut 재실행
3. 프로젝트 목록에서 ch{NN}_draft_{YYYYMMDD} 더블클릭
4. 자동 배치된 영상·음성·자막 확인 → 효과·BGM 만 수동 추가 → 렌더
```

## 옵션

| 옵션 | 동작 |
|---|---|
| `--no-subtitle` | 자막 주입 단계 스킵 (영상·음성만) |
| `--no-install` | 설치 단계 스킵 (워크스페이스에 빌드만) |
| `--font <path>` | 자막 폰트 경로 (default: `C:/Windows/Fonts/malgun.ttf`) |
| `--canvas-w <int>` / `--canvas-h <int>` | 캔버스 크기 (default: 1920×1080) |
| `--overwrite` | 동명 드래프트 덮어쓰기 (재설치) |

## 산출물

```
workspace/ch{NN}/draft/                              ← 빌드 결과 (워크스페이스 내)
├── draft_content.json
├── draft_meta_info.json
├── draft_cover.jpg
├── (부속 파일 8개 + 빈 폴더 7개)
└── Resources/

%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\ch{NN}_draft_{YYYYMMDD}\   ← 설치 결과
```

## 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| `%LOCALAPPDATA%\CapCut\...` 경로 없음 | CapCut 첫 실행/저장 안 함 | CapCut 실행 → 아무 프로젝트 저장 → 종료 → 재시도 |
| 드래프트 목록에 안 보임 | CapCut 캐시 | 작업관리자에서 `CapCut.exe` 까지 종료 후 재시작 |
| 더블클릭해도 안 열림 | 자막을 v1 (`inject_subtitles.py`) 으로 주입함 | `--overwrite` 로 재설치 (v2 가 자동 사용됨) |
| "비정상적인 경로" 에러 | path 필드들이 실제 위치와 불일치 | `install_draft.py` 가 자동 갱신 — 정상 절차로는 발생 안 함 |
| 이미지·오디오 개수 불일치 | `images/` 와 `audio/` 파일 수가 다름 | 양쪽 동일하게 맞추기 |

상세: [docs/OTHER-PC-SETUP.md](../docs/OTHER-PC-SETUP.md) §6

## 관련 파일

- [skills/build-capcut-draft/build_draft.py](../skills/build-capcut-draft/build_draft.py)
- [skills/build-capcut-draft/inject_subtitles_v2.py](../skills/build-capcut-draft/inject_subtitles_v2.py)
- [skills/build-capcut-draft/install_draft.py](../skills/build-capcut-draft/install_draft.py)
- [skills/build-capcut-draft/SKILL.md](../skills/build-capcut-draft/SKILL.md)
