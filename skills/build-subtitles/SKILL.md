---
name: build-subtitles
description: workspace/ch{NN}/script.json의 scenes[].narration_text를 한국어 SRT 자막으로 변환한다. 문장 단위 분절, narration_seconds 기반 타이밍 계산, UTF-8 BOM + CRLF 인코딩, 줄 길이·큐 길이 규칙 검증을 수행하고 편집 권장 목록을 제시한다. 씬별 SRT + 합본 SRT를 저장한다. 사용자가 "자막 만들어줘", "SRT 생성", "/weave-subtitle"라고 요청하면 이 스킬을 사용한다.
---

# 자막 생성 (Build Subtitles)

내레이션 텍스트를 CapCut 호환 SRT 자막 파일로 변환한다. 사람이 최종 검수·수정할 것을 전제로 한다.

## 사전 조건

- `workspace/ch{NN}/script.json` 이 존재해야 함 (`/weave-ingest` 선행)
- `knowledge/subtitle-style-guide.md` 의 규칙을 따른다

## 처리 단계

1. **script.json 로드**: `scenes[]` 의 `narration_text` 와 `narration_seconds` 수집.
2. **문장 분절**: `.`, `?`, `!`, `。` 경계로 1차 분할. 긴 문장은 접속사 경계에서 2차 분할.
3. **타이밍 계산**: 씬 내 각 큐 지속 시간 = `(cue_chars / scene_chars) × narration_seconds`. 씬 간은 `narration_seconds` 누적으로 전역 시각 산출.
4. **범위 조정 플래그**: 1.5초 미만/7초 초과 큐, 18자 초과 줄을 "편집 권장 목록" 에 기록.
5. **SRT 저장**: UTF-8 BOM + CRLF. 씬별(`ch{NN}_{SS}.srt`) + 합본(`ch{NN}_full.srt`).
6. **편집 포인트 리포트**: 사용자에게 규칙 위반 큐 목록을 경로와 함께 제시.

## 산출물

`workspace/ch{NN}/subtitles/` 에 씬별 SRT M개 + 합본 SRT 1개.

## 재실행 주의

재실행 시 `subtitles/` 의 파일을 **덮어쓴다**. 사람이 편집한 내용이 유실되므로, 재생성 전 사용자에게 백업 여부 확인.

## TODO (코웍 세션에서 구현)

문장 분절 알고리즘(한국어 특화), 타이밍 배분, SRT 직렬화(BOM·CRLF), 규칙 위반 감지는 차기 코웍 세션에서 구현한다. 이 파일은 스텁이다.
