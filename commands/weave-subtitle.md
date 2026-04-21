---
description: script.json의 narration_text에서 한국어 SRT를 생성한다. 씬별 SRT + 합본 SRT를 저장하고, 사람이 손봐야 할 편집 포인트를 제시한다.
argument-hint: "[챕터 번호]"
---

# /weave-subtitle

내레이션 텍스트를 SRT 자막으로 변환한다. **사람이 손볼 것을 전제**로 한다.

## 사전 조건

- `workspace/ch{NN}/script.json` 이 존재해야 함
- `/weave-ingest` 가 먼저 실행되어 있어야 함

## 실행 흐름

### Step 1: 내레이션 분절

각 씬의 `narration_text` 를 문장 단위로 분절:
- 문장 경계: `.`, `?`, `!`, `。`
- 접속사 경계: 긴 문장은 `그러나`, `하지만`, `그래서` 앞에서 선택적 분할
- 한 큐 최소 1.5초, 최대 7초 (범위 밖이면 병합/분할 제안)

### Step 2: 타이밍 계산

씬의 `narration_seconds` 를 문장별 글자수 비율로 배분:

```
cue_duration = (cue_chars / scene_chars) × narration_seconds
cue_gap = 0.1s  (겹침 방지)
```

씬 간 시작 시각은 이전 씬들의 `narration_seconds` 누적.

### Step 3: SRT 저장

인코딩: **UTF-8 BOM + CRLF**

```
workspace/ch{NN}/subtitles/
├── ch{NN}_{SS}.srt      # 씬별(1~M)
└── ch{NN}_full.srt      # 합본(전체 타임라인)
```

### Step 4: 편집 포인트 리포트

`knowledge/subtitle-style-guide.md` 의 규칙 위반을 찾아서 보고:

```
📝 자막 생성 완료: ch{NN}
   총 M개 씬, K개 큐, 예상 길이 T초

⚠ 편집 권장 큐 (N건)
  ch{NN}_02.srt #3: 22자 → 18자 초과 (줄바꿈 필요)
    "심리학 교수 스키너는 타자기 앞에 앉아"
  ch{NN}_05.srt #1: 0.8초 → 너무 짧음 (다음 큐와 병합 권장)
  ch{NN}_07.srt #4: 8.2초 → 너무 김 (분할 권장)

편집 위치: workspace/ch{NN}/subtitles/
완료 후 "계속" 또는 /weave-draft {NN}
```

## 편집 가이드

SRT 파일은 일반 텍스트 에디터에서 편집 가능. CapCut에서 다시 불러올 수 있으므로 자유롭게 수정.

- 한 줄 18자 초과 시: 자연스러운 어절 경계에 엔터 삽입
- 너무 짧은 큐: 앞/뒤 큐와 병합 (타임스탬프 조정)
- 너무 긴 큐: 문장 경계에서 분할 (중간 타임스탬프 계산)
- 조사(은·는·이·가) 앞에서 줄바꿈 **금지**

## 재실행

`/weave-subtitle {NN}` 을 다시 실행하면 `subtitles/` 를 **덮어쓴다**. 편집 내용이 사라지므로 주의. 재생성 전 백업 확인.
