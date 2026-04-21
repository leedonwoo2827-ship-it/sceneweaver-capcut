---
description: 상류 3개 프로젝트(ScriptForge/FlowGenie/TTS)에서 한 챕터의 산출물을 workspace/ch{NN}/로 수집한다. 누락 자산을 리포트한다.
argument-hint: "[챕터 번호] [--script-path <path>] [--images-dir <path>] [--audio-dir <path>]"
---

# /weave-ingest

챕터 하나의 자산을 `workspace/ch{NN}/` 로 모은다.

## 실행 흐름

### Step 1: 소스 경로 결정

**기본 경로**
- ScriptForge 출력: `D:\00work\260416-scriptforge\output\ch{NN}\ch{NN}_script.json`
- FlowGenie 이미지: 사용자에게 확인하거나 `--images-dir` 로 지정
- TTS 오디오: 사용자에게 확인하거나 `--audio-dir` 로 지정

**외부 스테이징 폴더 관례**
상류 3개 프로젝트가 없거나 파일을 수동으로 모은 경우, 다음 하위폴더 구조를 권장:

```
<staging-root>/
├── script/ch{NN}_script.json
├── images/   (구글드라이브 "이미지 로데이터" 등을 통째로 복사)
└── audio/    (구글드라이브 "음성 로데이터" 등을 통째로 복사)
```

호출 예:
```
/weave-ingest 1 \
  --script-path D:\cl150y\ch01\script\ch01_script.json \
  --images-dir D:\cl150y\ch01\images \
  --audio-dir D:\cl150y\ch01\audio
```

### Step 2: 워크스페이스 준비

- `workspace/ch{NN}/` 하위 폴더 생성: `images/`, `audio/`, `subtitles/`, `draft/`
- 이미 존재하면 사용자 확인: 덮어쓰기 / 건너뛰기 / 취소

### Step 3: 파일 수집

**공통 원칙**
- 소스 폴더의 원본은 절대 수정/이동/리네이밍하지 않는다. 복사만.
- 정규화(리네이밍)는 `workspace/ch{NN}/` 쪽 사본에만 적용.

**script.json**
- `--script-path`의 파일을 `workspace/ch{NN}/script.json` 으로 복사.

**이미지 (`images/`)** — 우선순위 판정
- 허용 확장자: `.png`, `.jpg`, `.jpeg` (대소문자 무시).
1. `ch{NN}_{SS}_*.{png,jpg,jpeg}` 패턴이 있으면 → 원본 파일명 그대로 복사.
2. 없고 **숫자로 시작하는 파일명**(`16.jpeg`, `16_alice_springs_1.jpeg`, `01.png` 등)만 있으면 → 앞쪽 숫자를 씬 번호로 해석해 `ch{NN}_` prefix를 붙여 복사. 예: `16_alice_springs_1.jpeg` → `ch01_16_alice_springs_1.jpeg`, `01.png` → `ch01_01.png`.
3. 두 방식이 혼재하면 사용자에게 어느 쪽을 쓸지 확인.

**오디오 (`audio/`)** — 우선순위 판정
1. `ch{NN}_{SS}_narration.{mp3,wav}` 패턴이 있으면 → 그대로 복사.
2. 없고 **순수 숫자 파일명**(`1.wav`, `01.wav`, `13.mp3` 등)만 있으면 → 숫자를 씬 번호로 해석, `ch{NN}_{SS}_narration.{원본확장자}`로 리네이밍 복사. 씬 번호 자리수는 `script.json`의 `scenes[].scene`과 일치.
3. 두 방식이 혼재하면 사용자에게 어느 쪽을 쓸지 확인.

### Step 4: 검증 & 리포트

`script.json` 의 `scenes[]` 와 수집된 파일 수를 비교:

```
📥 수집 리포트: ch{NN}
   스크립트: ✓
   이미지:   N/M 씬 (누락: S2, S5)        .jpeg 16건, .png 4건
   오디오:   N/M 씬 (누락: S5)             .wav 20건
   정규화:   오디오 13.wav → ch01_13_narration.wav (20건)

누락이 있으면:
  - FlowGenie로 돌아가 누락 씬 이미지 재생성
  - TTS로 돌아가 누락 씬 오디오 재생성
  - /weave-ingest 재실행
```

정규화가 일어난 항목은 "정규화" 라인에 요약한다(없으면 생략).

## 사용자 수정 대응

- "S2 이미지 파일명이 달라" → 실제 파일명을 물어보고 리네이밍 확인
- "다른 경로에서 가져와" → `--images-dir` 재지정
- "script.json이 구버전이야" → ScriptForge로 돌아가 재생성 안내

## 산출물

```
workspace/ch{NN}/
├── script.json
├── images/ch{NN}_{SS}_*.{png,jpg,jpeg}    (원본 확장자 유지)
├── audio/ch{NN}_{SS}_narration.{mp3,wav}  (원본 확장자 유지, 숫자명은 정규화됨)
├── subtitles/                             (빈 폴더, 다음 단계에서 채움)
└── draft/                                 (빈 폴더, 다음 단계에서 채움)
```
