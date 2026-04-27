# SceneWeaver-CapCut

ScriptForge의 마스터 대본과 FlowGenie/TTS의 산출물을 모아, **CapCut 8.x 데스크톱이 더블클릭만 하면 열리는 드래프트 폴더**를 생성하는 Claude Code 플러그인.

> **자매 레포**: [sceneweaver](https://github.com/leedonwoo2827-ship-it/sceneweaver) — 같은 상류 자산을 받아 **FFmpeg로 mp4를 직접 렌더**하는 버전. NLE 없이 완성 영상까지 끝내고 싶으면 그쪽.

> ✅ **v0.2.0 — 풀 자동화 검증 완료 (2026-04-27)**: 한 줄 명령으로 워크스페이스 자산 → CapCut 정상 로드 가능 드래프트. 자막 자동 트랙 배치 동작 (ch02: 이미지 23 + 오디오 23 + 자막 200 cue 검증 통과).

## 파이프라인 위치

```
StoryLens → ScriptForge → FlowGenie + TTS → [SceneWeaver-CapCut]
(상담/기획)  (대본 생성)   (이미지+음성)      (CapCut 드래프트)
```

- **상류**:
  - [ScriptForge](https://github.com/leedonwoo2827-ship-it/scriptforge): `ch{NN}_script.json`
  - FlowGenie: `ch{NN}_{SS}_*.{png,jpg,jpeg}`
  - TTS: `ch{NN}_{SS}_narration.{mp3,wav}`
- **하류**: CapCut 8.5.0+ 데스크톱. 사용자가 더블클릭 → 자동 배치된 영상·음성·자막 → 효과·전환·BGM 만 수동 추가 → 렌더.

## 설치

### 옵션 A — Claude Code 플러그인 (슬래시 커맨드)

```
/plugin marketplace add leedonwoo2827-ship-it/sceneweaver-capcut
/plugin install sceneweaver-capcut@sceneweaver-capcut
```

설치 후 `/weave`, `/weave-ingest`, `/weave-subtitle`, `/weave-draft` 활성화.
업데이트: `/plugin update sceneweaver-capcut@sceneweaver-capcut`.

### 옵션 B — 직접 clone (Python 만 사용)

```bash
git clone https://github.com/leedonwoo2827-ship-it/sceneweaver-capcut
cd sceneweaver-capcut
# Python 3.9+ 만 있으면 됨, 외부 의존성 없음
```

## 사전 준비

1. **CapCut 8.5.0 이상** 데스크톱 설치 (Windows 우선 지원)
2. **CapCut 을 한 번이라도 실행해서 아무 프로젝트라도 저장** — `%LOCALAPPDATA%\CapCut\...\com.lveditor.draft\` 디렉터리와 `root_meta_info.json` 이 생성되어야 함. 처음 깐 직후엔 없음.
3. **Python 3.9+**
4. **상류 자산** — ScriptForge/FlowGenie/TTS 출력 또는 외부 스테이징 폴더에 모은 자료

처음 받으신 분은 **[docs/OTHER-PC-SETUP.md](docs/OTHER-PC-SETUP.md)** 의 단계별 절차 권장.

## 자산 폴더 구조

**clone 한 레포 폴더 안의 `workspace/ch{NN}/` 에 배치를 권장** — 슬래시 커맨드는 `--workspace` 옵션을 안 받고, `.gitignore` 가 `workspace/` 를 제외하므로 깃에 안 올라갑니다. 외부 드라이브에 두려면 Python 직접 호출 + `--workspace <경로>` 만 가능.

```
<clone 위치>\sceneweaver-capcut\workspace\ch{NN}\
├── images/             ← *.jpeg / *.jpg / *.png (정렬된 파일명)
├── audio/              ← *.wav (이미지와 같은 개수)
└── subtitles/          ← (선택) *.srt
```

- 이미지·오디오 개수 일치, 정렬 순서로 1:1 페어링
- 자막은 `ch{NN}_full.srt` 합본 또는 단일 SRT

상세: [docs/OTHER-PC-SETUP.md §2](docs/OTHER-PC-SETUP.md)

## 실행 — v0.2 자동화

### 옵션 A — Claude Code 슬래시 커맨드 (권장)

플러그인 설치 후 Claude Code 안에서:

```
/weave-ingest 02       # 상류 자산 → workspace/ch02/
/weave-subtitle 02     # SRT 생성 → 사람이 편집
/weave-draft 02        # 빌드 + 자막 주입 + CapCut 설치 (한 방)
```

또는 전체 오케스트레이션:

```
/weave 02              # ingest → subtitle → (사람 편집 대기) → draft + install
```

`/weave-draft` 옵션:
- `--no-subtitle` — 자막 주입 스킵
- `--no-install` — CapCut 설치 스킵 (워크스페이스 빌드만)
- `--overwrite` — 동명 드래프트 덮어쓰기 (재설치)
- `--font <path>` — 자막 폰트 변경
- `--canvas-w <int>` / `--canvas-h <int>` — 캔버스 크기 변경

### 옵션 B — Python 직접 호출

```bash
# 1. 빌드
python skills/build-capcut-draft/build_draft.py 02

# 2. 자막 주입 (선택)
python skills/build-capcut-draft/inject_subtitles_v2.py 02

# 3. CapCut 으로 설치
python skills/build-capcut-draft/install_draft.py 02
```

### 공통 후속 절차

→ CapCut 완전 종료 후 재실행 → 프로젝트 목록에서 `ch02_draft_{YYYYMMDD}` 더블클릭 → 자동 배치된 영상·음성·자막 확인 → 효과·BGM 만 수동 추가하여 렌더.

## 산출물

```
workspace/ch{NN}/draft/                       ← build_draft.py 결과
├── draft_content.json                        # 타임라인 본체
├── draft_meta_info.json                      # 메타·자료 인덱스
├── draft_cover.jpg
├── (부속 8개 + 빈 폴더 7개)
└── Resources/                                # 자산 사본
    ├── ch{NN}_*.jpeg
    ├── *.wav
    └── ch{NN}_full.srt   (자막 주입 시)
```

설치 후 위치:
```
%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\ch{NN}_draft_{YYYYMMDD}\
```

## 현재 상태 (v0.2.0)

| 항목 | 상태 |
|---|---|
| 프로젝트 뼈대 | ✅ |
| 상류 자산 ingest | ✅ |
| SRT 자막 생성 + 편집 개입 | ✅ |
| CapCut 8.x 스키마 분석 | ✅ [knowledge/capcut8-schema.md](knowledge/capcut8-schema.md) |
| **풀 자동 빌더** (`build_draft.py`) | ✅ 2026-04-27 검증 |
| **자동 설치 + `root_meta_info.json` 갱신** (`install_draft.py`) | ✅ 2026-04-27 검증 |
| **자막 자동 트랙 배치** (`inject_subtitles_v2.py`) | ✅ 2026-04-27 검증 (5필드 fix) |
| ch02 풀 검증 (이미지 23 + 오디오 23 + 자막 200) | ✅ CapCut 8.5.0 정상 로드 |
| `transition_hint` / `mood` / `era` → CapCut 효과 ID 매핑 | ⏳ v0.3 (추가 샘플 필요) |
| BGM 트랙 자동 추가 | ⏳ v0.3 |
| Mac 지원 | ⏳ 미검증 |

## 왜 별도 레포인가

원래 sceneweaver (v0.2)는 CapCut 4.x 스키마를 가정했지만, CapCut 8.5.0 에서 **"비정상적인 경로" 에러** 로 거부됨이 확인됨 (2026-04-20). v0.3 에서 sceneweaver 는 FFmpeg 직렌더로 방향 전환했고, CapCut 타겟을 여전히 원하는 사용 사례를 위해 이 레포(`sceneweaver-capcut`)를 분기 생성.

- **sceneweaver**: `ch{NN}.mp4` 한 파일 → 바로 업로드/배포
- **sceneweaver-capcut** (이 레포): `draft/` 폴더 → CapCut 8.x 더블클릭 → 편집

## 문제 해결

- **드래프트가 목록에 안 보임** — `install_draft.py` 가 `root_meta_info.json` 의 `all_draft_store[]` 에 엔트리를 추가했는지 확인. 또한 CapCut 을 작업관리자 프로세스까지 완전 종료 후 재시작.
- **더블클릭해도 안 열림** — 자막 주입을 v1 (`inject_subtitles.py`) 으로 한 경우. v2 (`inject_subtitles_v2.py`) 로 다시 주입 후 `install_draft.py --overwrite` 재실행.
- **"비정상적인 경로" 에러** — `install_draft.py` 가 path 필드들을 자동 갱신하니 정상 절차로 설치하면 발생 안 함. 발생 시 `draft_content.json` / `draft_meta_info.json` 의 `file_Path` 들을 확인.
- **자막이 깨진다** — SRT 인코딩 UTF-8 BOM + CRLF (또는 LF), 타이밍 `HH:MM:SS,mmm` 형식.
- **CapCut 디렉터리가 없다고 나옴** — CapCut 을 한 번도 실행 안 한 상태. 실행 → 아무 프로젝트라도 저장 → 종료 → 재시도.

상세 트러블슈팅: [docs/OTHER-PC-SETUP.md](docs/OTHER-PC-SETUP.md) §6.

## 다른 PC 에서 처음 쓰시나요

**[docs/OTHER-PC-SETUP.md](docs/OTHER-PC-SETUP.md)** 에 처음 clone/pull 받은 분을 위한 단계별 가이드가 있습니다. CapCut 첫 실행 체크리스트부터 자동화 한 줄 실행, 트러블슈팅까지 전부.

## 라이선스

MIT
