---
name: ingest-assets
description: ScriptForge의 마스터 대본 JSON과 FlowGenie의 이미지, TTS의 내레이션 오디오를 한 챕터 단위로 workspace/ch{NN}/ 아래에 수집한다. 파일명은 상류의 ch{NN}_{SS}_* 패턴을 그대로 승계하고, script.json의 씬 수와 실제 파일 수를 비교하여 누락 자산을 리포트한다. 사용자가 "자산 수집", "드래프트 준비", "/weave-ingest"라고 요청하면 이 스킬을 사용한다.
---

# 자산 수집 (Ingest)

상류 3개 프로젝트의 산출물을 한 챕터 워크스페이스로 모은다.

## 사전 조건

- 챕터 번호(1 이상 정수) 가 인자로 주어져야 함
- 최소한 ScriptForge의 `ch{NN}_script.json` 은 존재해야 함
- FlowGenie 이미지·TTS 오디오는 부분 누락 가능 (경고만 하고 진행)

## 처리 단계

1. **소스 경로 확인**: 기본 ScriptForge 경로(`D:\00work\260416-scriptforge\output\ch{NN}\`) 부터 확인, 없으면 사용자에게 물어본다. 외부 스테이징 폴더 사용 시 `--script-path`, `--images-dir`, `--audio-dir` 로 분리 지정.
2. **워크스페이스 생성**: `workspace/ch{NN}/` + 하위 `images/`, `audio/`, `subtitles/`, `draft/` 폴더.
3. **script.json 복사**: 원본 수정 금지, 복사본만 사용. 대상 파일명은 `script.json`.
4. **이미지 수집** (아래 우선순위로 판정):
   - 허용 확장자: `.png`, `.jpg`, `.jpeg` (대소문자 무시).
   1. `ch{NN}_{SS}_*.{png,jpg,jpeg}` 패턴이 있으면 → 원본 파일명 그대로 `images/`로 복사.
   2. 없고 **숫자로 시작하는 파일명**(`16.jpeg`, `16_alice_springs_1.jpeg`, `01.png` 등)만 있으면 → 앞쪽 숫자를 씬 번호로 해석해 `ch{NN}_` prefix를 붙여 복사. 예: `16_alice_springs_1.jpeg` → `ch01_16_alice_springs_1.jpeg`, `01.png` → `ch01_01.png`. 씬 번호 자리수는 `script.json`의 `scenes[].scene`과 일치.
   3. 두 방식이 혼재하면 사용자에게 어느 쪽을 쓸지 확인.
5. **오디오 수집** (아래 우선순위로 판정):
   1. `ch{NN}_{SS}_narration.{mp3,wav}` 패턴이 있으면 → 그대로 `audio/`로 복사.
   2. 없고 소스 폴더에 **순수 숫자 파일명**(`1.wav`, `01.wav`, `13.mp3` 등)만 있으면 → 숫자를 씬 번호로 해석해 `ch{NN}_{SS}_narration.{원본확장자}` 형태로 **리네이밍 복사**. 씬 번호 자리수는 `script.json`의 `scenes[].scene`과 일치시킨다(예: scene 값이 `1`이면 `ch01_1_narration.wav`, `01`이면 `ch01_01_narration.wav`).
   3. 두 방식이 **혼재**하면 사용자에게 어느 쪽을 쓸지 확인.
6. **원본 불변**: 소스 폴더의 어떤 파일도 리네이밍/이동/삭제하지 않는다. 정규화는 `workspace/ch{NN}/` 쪽 사본에만 적용.
7. **검증 리포트**: script.json의 `scenes[].scene` 번호와 수집된 파일들의 씬 번호를 비교해 누락 보고. 리네이밍이 일어난 경우 요약 한 줄(예: `오디오: 13.wav → ch01_13_narration.wav (20건 정규화됨)`) 포함.

## 산출물

`workspace/ch{NN}/` 아래에 script.json + images/ + audio/ + 빈 subtitles/ + 빈 draft/.
