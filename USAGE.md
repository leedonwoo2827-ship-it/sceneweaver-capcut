# SceneWeaver-CapCut 사용설명서

커맨드 중심 실행 가이드. 프롬프트 예문과 함께.

> 이 문서는 **CapCut 8.5.0+ 설치 + 플러그인 설치**를 전제로 작성됨.
> 플러그인: `/plugin marketplace add leedonwoo2827-ship-it/sceneweaver-capcut` → `/plugin install sceneweaver-capcut@sceneweaver-capcut`
> 설치 후 `/weave`, `/weave-ingest`, `/weave-subtitle`, `/weave-draft` 활성화.
>
> ⚠ v0.1은 CapCut 8.x 스키마 분석 진행 중. 현재 `/weave-draft` 는 인터페이스만 있고 실체 빌드는 다음 세션에서 구현.

---

## 빠른 시작 (한 챕터 조립)

```
/weave-ingest 3
     ↓
/weave-subtitle 3
     ↓
(사람 편집: workspace/ch03/subtitles/*.srt)
     ↓
/weave-draft 3 --install
```

또는 한 번에:

```
/weave 3
```

(각 단계에서 확인 요청 — 자동으로 넘어가지 않음)

---

## 커맨드별 상세

### 1. `/weave-ingest {챕터번호}` — 자산 수집

**하는 일**: ScriptForge의 `script.json`, FlowGenie의 이미지, TTS의 오디오를 `workspace/ch{NN}/` 로 모은다. 누락 자산을 보고한다.

**기본 실행**:
```
/weave-ingest 3
```

**경로를 직접 지정하고 싶을 때** (프롬프트 예문):

```
/weave-ingest 3
ScriptForge 경로는 D:\00work\260416-scriptforge\output\ch03\ch03_script.json 으로,
이미지는 D:\flowgenie\output\ch03\ 에서,
오디오는 D:\voice-harness\output\ch03\ 에서 가져와줘.
```

**누락 자산이 있을 때 (예상 응답)**:
```
📥 수집 리포트: ch03
   스크립트: ✓
   이미지:   5/7 씬 (누락: S3, S6)
   오디오:   7/7 씬 ✓

계속할까요? 아니면 FlowGenie에서 S3, S6 재생성 후 다시 실행할까요?
```

이 때 선택:
- "계속" → 일단 있는 자산만으로 다음 단계 진행 (권장 X)
- "멈춰. FlowGenie 다시 돌리고 올게" → 작업 중단

**후속 프롬프트 예문**:
- "누락된 씬 번호만 한번 더 확인해줘"
- "script.json의 씬 수하고 이미지/오디오 개수를 나란히 표로 보여줘"

---

### 2. `/weave-subtitle {챕터번호}` — 자막 생성

**하는 일**: `script.json`의 `narration_text` 를 **씬별 SRT 파일**로 변환한다. `workspace/ch{NN}/subtitles/` 에 저장.

**⚠ 자막 폴더는 이 단계에서 생성됨** — `/weave-ingest` 시점에 빈 폴더만 만들어두고, 실제 SRT 파일은 여기서 채워진다.

**기본 실행**:
```
/weave-subtitle 3
```

**생성 결과**:
```
workspace/ch03/subtitles/
├── ch03_01.srt       ← 씬 1 자막 (로컬 타임: 0초부터)
├── ch03_02.srt       ← 씬 2 자막
├── ...
├── ch03_07.srt
└── ch03_full.srt     ← 합본 (전역 타임라인)
```

**예상 응답**:
```
📝 자막 생성 완료: ch03
   7개 씬, 42개 큐, 예상 길이 180초

⚠ 편집 권장 큐 (3건)
  ch03_02.srt #3: 22자 → 18자 초과 (줄바꿈 필요)
    "심리학 교수 스키너는 타자기 앞에 앉아"
  ch03_05.srt #1: 0.8초 → 너무 짧음 (다음 큐와 병합 권장)
  ch03_07.srt #4: 8.2초 → 너무 김 (분할 권장)

편집 위치: workspace/ch03/subtitles/
완료 후 /weave-draft 3
```

**자주 쓰는 후속 프롬프트 예문**:

```
ch03_02.srt 3번 큐 "심리학 교수 스키너는 타자기 앞에 앉아"
"앉아" 앞에서 줄바꿈 해줘.
```

```
편집 권장 큐 3개를 다 자동으로 고쳐줘.
18자 초과는 어절 경계에서 줄바꿈,
너무 짧은 건 앞 큐와 병합,
너무 긴 건 문장 경계에서 분할.
```

```
ch03_05.srt 첫 큐와 두번째 큐를 하나로 합쳐줘.
타이밍은 첫 큐의 시작 시각부터 두번째 큐의 끝 시각까지.
```

```
합본 SRT(ch03_full.srt)를 다시 만들어줘.
씬별 파일에서 수정한 내용 반영해서.
```

---

### (자동화 아님 — 사람 개입)

에디터로 `subtitles/` 열어서 눈으로 확인 + 수정. VS Code라도 `.srt` 는 기본 편집 가능.

체크 포인트:
- 한 줄 18자 초과? → 어절 경계에서 엔터
- 조사(은/는/이/가/을/를) 앞에 엔터가 있으면? → 앞으로 옮기기
- 너무 짧은 큐(1.5초 미만)? → 앞/뒤와 병합
- 너무 긴 큐(7초 초과)? → 문장 경계에서 분할

수정 끝나면 **Claude에게 "계속" 또는 `/weave-draft 3`** 라고 말함.

---

### 3. `/weave-draft {챕터번호}` — CapCut 8.x 드래프트 빌드 (v0.1 스텁)

**하는 일**: 편집된 SRT + 이미지 + 오디오 + scene_meta → CapCut 8.x 드래프트 폴더. `draft_content.json` + `draft_meta_info.json` + v8.x 부속 파일 + `Resources/` 구성.

> v0.1은 스키마 분석 진행 중. 실체 빌드는 다음 세션.

**기본 실행**:
```
/weave-draft 3
```

**자동 설치 옵션**:
```
/weave-draft 3 --install
```
→ `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\` 자동 복사. CapCut 재시작 → 드래프트 목록에서 열기.

**예상 응답 (구현 후)**:
```
✓ 드래프트 생성 완료
  위치: D:\cl150y\ch03\workspace\ch03\draft\
  드래프트 ID: {UUID}
  폴더명: ch03_draft_{YYYYMMDD}_{UUID단축형}

CapCut 8.x에서 열기:
  1. CapCut 완전 종료
  2. 아래 폴더를 %LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\ 에 복사
  3. CapCut 재시작 → 프로젝트 목록에 표시됨
```

**자주 쓰는 후속 프롬프트 예문**:

```
드래프트 다시 빌드하되, 1번 씬 전환효과를 페이드 인 대신
디졸브로 바꿔줘. script.json 의 transition_hint 수정.
```

```
draft_content.json 을 열어서 자막 트랙 위치를 화면 하단에서
중앙 하단으로 (y 오프셋 -300) 바꿔줘.
```

```
씬 3번 이미지를 image2.png 대신 image2_v2.png 로 바꾸고
드래프트를 다시 빌드해줘.
```

---

### 4. `/weave {챕터번호}` — 전체 오케스트레이션

**하는 일**: 위 세 단계를 순차 실행하되 **각 단계마다 확인**한다. 자막 편집 단계에서는 **대기**한다.

**기본 실행**:
```
/weave 3 --install
```

**실행 흐름**:
```
Step 1: /weave-ingest 3
    → 수집 리포트 제시 → 사용자 확인

Step 2: /weave-subtitle 3
    → 자막 생성 + 편집 권장 목록 제시
    → "subtitles/ 에서 수정 후 '계속' 해주세요" 메시지

    [사람이 SRT 편집]

    사용자: "계속" 또는 "수정 끝났어"

Step 3: /weave-draft 3 --install
    → CapCut 8.x 드래프트 폴더 생성 + 자동 설치
```

**중간에 되돌아가기**:

```
"자막 다시 뽑아줘" → Step 2 재실행
"ch03_02 이미지만 다시 받아올게" → Step 1로 돌아가 S2만 재수집
```

---

## 유용한 후속 프롬프트 모음

### 자막 일괄 작업
```
workspace/ch03/subtitles/ 안의 모든 SRT에서
마침표 뒤에 공백이 없는 곳 찾아서 고쳐줘.
```

```
전체 자막을 검토하고 맞춤법 오류만 리포트해줘. 수정은 아직 하지 말고.
```

```
ch03_full.srt 에서 한 큐가 5초를 넘는 것들만 리스트로 보여줘.
```

### 합본(merge) 관련
```
씬별 SRT 7개를 합쳐서 ch03_full.srt 로 만들어줘.
각 씬의 시작 시각은 이전 씬들의 narration_seconds 누적값으로.
큐 번호는 전역으로 1부터 다시 매기고.
```

```
ch03_full.srt 와 개별 씬 SRT 들의 타이밍이 일치하는지 검증해줘.
어긋나는 큐가 있으면 리포트.
```

### 드래프트 검증
```
draft/draft_content.json 과 draft_meta_info.json 을 열어서
1) 드래프트 UUID가 폴더명과 매칭되는지
2) Resources/ 안의 파일들이 tracks 에서 모두 참조되고 있는지
3) 참조되지 않는 파일이나 존재하지 않는 파일 참조가 있는지
검증 리포트 만들어줘.
```

### 챕터 전체 일괄 처리 (여러 챕터)
```
ch01 부터 ch07 까지 /weave 를 순차 실행해줘.
각 챕터의 자막 편집 단계는 일단 스킵(자동 추정치 그대로 사용),
최종 드래프트 7개까지 다 만들고 리포트.
```

---

## 문제 해결 프롬프트

### 자산 누락
```
workspace/ch03/images/ 에 있는 파일명과
script.json 의 scenes[].image_filename 을 비교해서
어긋나는 게 있는지 봐줘.
```

### SRT 인코딩 깨짐
```
ch03_full.srt 를 UTF-8 BOM + CRLF 로 다시 저장해줘.
```

### CapCut에서 드래프트가 안 열릴 때
```
draft/draft_content.json 과 draft_meta_info.json 을 열어서
내 CapCut 버전(톱니바퀴 > 버전)에서 요구하는 필수 필드가 다 있는지 판단해줘.
샘플은 _assetst/0421/ 참고.
```

### "비정상적인 경로" 에러
```
드래프트 폴더명과 draft_meta_info.json 의 드래프트 UUID가 일치하는지,
Resources/ 참조 경로가 상대경로로 되어있는지 확인해줘.
```

---

## 체크리스트 (챕터 시작 전)

- [ ] `ch{NN}_script.json` 이 있음 (ScriptForge 기본 경로 또는 스테이징 `script/` 하위)
- [ ] 이미지 `ch{NN}_{SS}_*.{png,jpg,jpeg}` 씬 수만큼 있음
- [ ] 내레이션 `ch{NN}_{SS}_narration.{mp3,wav}` 또는 `{씬번호}.{mp3,wav}` 씬 수만큼 있음 (순수 숫자명은 ingest에서 자동 정규화)
- [ ] CapCut 8.5.0+ 데스크톱 설치됨
- [ ] Claude Code에 sceneweaver-capcut 플러그인 설치됨 (`/plugin list` 로 확인)

---

## 외부 스테이징 폴더에서 실행하기

상류 3개 프로젝트를 쓰지 않고, 구글드라이브 등에서 받은 자산을 수동으로 모은 경우. 예시 경로 `D:\cl150y\ch01\`.

### 권장 레이아웃

```
D:\cl150y\ch01\
├── script\
│   └── ch01_script.json
├── images\                   ← 이미지 로데이터 폴더 통째 복사
│   ├── ch01_01_*.jpeg
│   ├── ...
│   └── ch01_20_*.jpeg
└── audio\                    ← 음성 로데이터 폴더 통째 복사
    ├── 01.wav  (또는 1.wav)
    ├── ...
    └── 20.wav
```

- 이미지 확장자는 `.png`/`.jpg`/`.jpeg` 모두 허용.
- 오디오가 `13.wav`처럼 순수 숫자명이어도 됨 — ingest가 `ch01_13_narration.wav`로 정규화해 workspace에 복사.
- 원본 파일은 그대로 보존됨.

### 실행 순서

```
/weave-ingest 1 --script-path D:\cl150y\ch01\script\ch01_script.json --images-dir D:\cl150y\ch01\images --audio-dir D:\cl150y\ch01\audio
```
→ 수집 리포트(정규화 요약 포함) 확인 → "계속"

```
/weave-subtitle 1
```
→ SRT 생성 → `workspace\ch01\subtitles\` 에서 사람 편집 → "수정 끝났어"

```
/weave-draft 1
```
또는 바로 설치:
```
/weave-draft 1 --install
```

한 방에:
```
/weave 1 --script-path D:\cl150y\ch01\script\ch01_script.json --images-dir D:\cl150y\ch01\images --audio-dir D:\cl150y\ch01\audio
```
(단계 사이에 확인 요청이 들어옴)
