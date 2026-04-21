# SceneWeaver-CapCut

ScriptForge의 마스터 대본과 FlowGenie/TTS의 산출물을 모아, **CapCut 8.x 데스크톱이 직접 열 수 있는 드래프트 폴더**를 생성하는 Claude Code 플러그인.

> **자매 레포**: [sceneweaver](https://github.com/leedonwoo2827-ship-it/sceneweaver) — 같은 상류 자산을 받아 **FFmpeg로 mp4를 직접 렌더**하는 버전. NLE 없이 완성 영상까지 끝내고 싶으면 그쪽.
>
> ⚠ **v0.1 — 스키마 분석 진행 중**: 현재 빌더는 인터페이스 명세와 뼈대만 있습니다. CapCut 8.5.0 샘플 JSON을 기반으로 실체 빌드 로직을 구현하는 것이 다음 작업.

## 파이프라인 위치

```
StoryLens → ScriptForge → FlowGenie + TTS → [SceneWeaver-CapCut]
(상담/기획)  (대본 생성)   (이미지+음성)      (CapCut 드래프트)
```

- **상류**:
  - [ScriptForge](https://github.com/leedonwoo2827-ship-it/scriptforge): `ch{NN}_script.json`
  - FlowGenie: `ch{NN}_{SS}_*.{png,jpg,jpeg}`
  - TTS: `ch{NN}_{SS}_narration.{mp3,wav}`
- **하류**: CapCut 8.5.0+ 데스크톱. 사용자가 드래프트 폴더를 열어 최종 편집·렌더.

## 설치

```
/plugin marketplace add leedonwoo2827-ship-it/sceneweaver-capcut
/plugin install sceneweaver-capcut@sceneweaver-capcut
```

설치 후 `/weave`, `/weave-ingest`, `/weave-subtitle`, `/weave-draft` 커맨드 활성화. 업데이트: `/plugin update sceneweaver-capcut@sceneweaver-capcut`.

## 사전 준비

1. **CapCut 8.5.0 이상** 데스크톱 설치 (Windows/Mac)
2. **상류 자산** — ScriptForge/FlowGenie/TTS 출력을 직접 쓰거나, 외부 스테이징 폴더에 수동으로 모아서 사용
3. **Claude Code** (이 플러그인이 도는 환경)

## 폴더 구조

### 최초 (ingest 실행 전 — 외부 스테이징 폴더)

상류 3개 프로젝트를 거치지 않고 구글드라이브 등에서 받은 자산을 수동으로 모은 경우의 원본 보관 구조. 예: `D:\cl150y\ch02\`.

```
D:\cl150y\ch02\
├── script\ch02_script.json
├── images\                      ← 이미지 로데이터
│   ├── ch02_01_*.jpeg
│   ├── ...
│   └── ch02_20_*.jpeg
└── audio\                       ← 음성 로데이터
    ├── 01.wav  (또는 1.wav)
    ├── ...
    └── 20.wav
```

ingest가 `.jpeg`/`.wav`/숫자 전용 이름을 자동 정규화.

### 드래프트 빌드 후 (`/weave-draft` 실행 후 예정)

```
workspace/ch02/
├── script.json
├── images/, audio/, subtitles/
└── draft/                                    ← ★ CapCut 드래프트
    ├── draft_content.json                    (v8.x 메인)
    ├── draft_meta_info.json
    ├── draft_cover.jpg
    ├── (v8.x 부속 파일들)
    └── Resources/
        ├── ch02_{SS}_image.jpeg
        ├── ch02_{SS}_narration.wav
        └── ch02_{SS}.srt
```

## 실행 순서 (v0.1 — 인터페이스 기준)

**1단계 — 자산 수집**
```
/weave-ingest 2 --script-path D:\cl150y\ch02\script\ch02_script.json --images-dir D:\cl150y\ch02\images --audio-dir D:\cl150y\ch02\audio
```

**2단계 — 자막 생성**
```
/weave-subtitle 2
```
→ `workspace/ch02/subtitles/` SRT 편집 → "수정 끝났어"

**3단계 — CapCut 드래프트 빌드**
```
/weave-draft 2 --install
```
→ `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\` 자동 복사. CapCut 재시작 → 드래프트 목록에서 열기.

**한 방 실행**
```
/weave 2 --script-path ... --images-dir ... --audio-dir ... --install
```

## 현재 상태 (v0.1)

| 항목 | 상태 |
|---|---|
| 프로젝트 뼈대 | ✅ sceneweaver v0.3에서 분기 |
| 상류 자산 ingest (`.jpeg`/`.wav`/숫자명 정규화) | ✅ 기존 로직 승계 |
| SRT 자막 생성 + 편집 개입 | ✅ 기존 로직 승계 |
| CapCut 8.x 샘플 JSON 확보 | ✅ [`_assetst/0421/`](_assetst/0421/) |
| CapCut 8.x 스키마 분석 | 🔄 진행 중 — [knowledge/capcut8-schema.md](knowledge/capcut8-schema.md) |
| `draft_content.json` 필드 매핑 | 🔄 샘플 기반 수동 조립 성공 (2026-04-21) |
| **`root_meta_info.json` 전역 레지스트리 발견** | ✅ 드래프트 목록에 뜨려면 `all_draft_store` 에 엔트리 추가 필요 |
| ch01 실빌드 → CapCut 8.5.0 열기 검증 | ✅ **성공 (2026-04-21)** — 씬 20 + 오디오 20 타임라인 정상, 길이 8:01 |
| 자막 자동 import | ⏳ 다음 세션 (현재는 CapCut UI에서 Import → Subtitle 수동) |
| `build-capcut-draft` v0.2 자동화 | ⏳ 다음 세션 |

## 왜 별도 레포인가

원래 sceneweaver (v0.2)는 CapCut 4.x 스키마를 가정했지만, CapCut 8.5.0 에서 **"비정상적인 경로" 에러**로 드래프트를 거부함이 확인됨(2026-04-20). v0.3에서 sceneweaver는 FFmpeg 직렌더로 완전히 방향을 바꿨고, CapCut 타겟을 여전히 원하는 사용 사례를 위해 **이 레포(`sceneweaver-capcut`)** 를 분기 생성했다. 두 플러그인은 상류(ingest, subtitle)를 공유하지만 하류가 다르다:

- **sceneweaver**: `ch{NN}.mp4` 한 파일 → 바로 업로드/배포
- **sceneweaver-capcut** (이 레포): `draft/` 폴더 → CapCut 8.x에서 열어 편집

## 문제 해결

- **"비정상적인 경로" 에러** — CapCut 4.x 스키마로 만든 드래프트는 8.x에서 열리지 않음. 이 레포가 해결하려는 문제.
- **자막이 깨진다** — SRT 인코딩 UTF-8 BOM + CRLF, 타이밍 `HH:MM:SS,mmm` 형식 확인.
- **드래프트 목록에 안 보임** — CapCut 완전 종료(작업관리자 프로세스까지) 후 재시작.

## 라이선스

MIT
