# scene_meta → CapCut 효과 매핑

ScriptForge의 `scene_meta` 필드를 CapCut 드래프트의 전환·필터·컬러 그레이딩 설정으로 변환하는 매핑 테이블.

> **주의**: CapCut 내부 효과 ID 문자열은 버전별로 변동이 크다. 아래 "CapCut 값" 열은 차기 세션에서 실제 드래프트 JSON을 열어보며 교정해야 한다.

## transition_hint → 전환 효과

| scene_meta.transition_hint | 의미 | CapCut 전환 이름 | 지속(μs) |
|---|---|---|---|
| `fade_in` | 페이드 인 | 페이드 인 | 500000 |
| `fade_out` | 페이드 아웃 | 페이드 아웃 | 500000 |
| `crossfade` | 디졸브 | 디졸브 | 800000 |
| `cut` | 컷 | (전환 없음) | 0 |
| `wipe` | 와이프 | 사이드 와이프 | 600000 |
| `zoom_in` | 줌 인 | 확대 | 700000 |
| `zoom_out` | 줌 아웃 | 축소 | 700000 |
| `none` / `null` | 기본 | `video_meta.default_transition` 사용 | — |

미매핑 값이 오면 `default_transition`로 폴백.

## mood → 컬러 그레이딩

| scene_meta.mood | 톤 | CapCut 필터/조정 | 비고 |
|---|---|---|---|
| `tension` | 차가움·긴장 | 색온도 -10, 대비 +15, 채도 -5 | 어두운 장면 |
| `warm` | 따뜻함 | 색온도 +10, 밝기 +5, 채도 +10 | 회상·감동 |
| `neutral` | 중립 | 기본값 | 다큐멘터리 기본 |
| `melancholy` | 쓸쓸함 | 채도 -20, 대비 -5, 섀도우 +10 | 발라드·에필로그 |
| `hopeful` | 희망적 | 밝기 +10, 채도 +15, 하이라이트 +5 | 해소·결말 |
| `dramatic` | 극적 | 대비 +25, 섀도우 -10, 비네트 | 클라이맥스 |

## era → 필터 프리셋

| scene_meta.era | 시대 | CapCut 필터 제안 |
|---|---|---|
| `1900s`, `1910s` | 초기 | 세피아 + 그레인 |
| `1920s`~`1940s` | 전간기 | 세피아 또는 흑백 |
| `1950s`, `1960s` | 전후 | 흑백 필름 + 약간의 그레인 |
| `1970s` | 70년대 | 색 바램(고채도→저채도) |
| `1980s`, `1990s` | 현대 | 비디오 룩 |
| `2000s` 이후 | 디지털 | 기본 (필터 없음) |
| 미지정 / `null` | — | 필터 없음 |

## bgm_hint → BGM 슬롯

BGM은 **자동 선택하지 않는다**. 대신 `draft_info.json` 에 빈 오디오 트랙 슬롯을 만들어 사람이 CapCut에서 채우도록 한다.

| scene_meta.bgm_hint | 슬롯 이름 |
|---|---|
| `suspenseful_piano` | "BGM: 서스펜스 피아노" |
| `ambient_strings` | "BGM: 앰비언트 현악" |
| `upbeat` | "BGM: 경쾌한" |
| `melancholy_piano` | "BGM: 멜랑콜리 피아노" |
| 그 외 | "BGM: (사용자 지정)" |

## subtitle, text_overlay

- `scene_meta.subtitle` — 씬 시작 지점에 **상단 자막 오버레이**로 3초간 표시
  - 위치: 화면 상단 중앙 (y 오프셋: +350)
  - 폰트 크기: 36 (메인 자막보다 작게)
  - 배경: 반투명 검정 50%
- `scene_meta.text_overlay` — 씬 전 구간에 걸쳐 표시하는 텍스트 레이어 (선택)
  - 위치·스타일은 값에 따라 다름. 기본은 상단 좌측.

## video_meta → 드래프트 전역 설정

| video_meta 필드 | draft_info.json |
|---|---|
| `aspect_ratio: "16:9"` | `canvas_config: {width:1920, height:1080}` |
| `aspect_ratio: "9:16"` | `canvas_config: {width:1080, height:1920}` (쇼츠용) |
| `opening_title` | 첫 트랙에 3초 타이틀 카드 삽입 |
| `closing_text` | 마지막 트랙에 2초 엔드 카드 삽입 |
| `default_transition` | transition_hint 없는 씬에 적용 |
| `bgm_track` | 전역 BGM 트랙 (null이면 빈 슬롯) |

## 차기 세션에서 교정할 항목 (TODO)

1. CapCut 전환 효과의 **실제 내부 ID** (문서의 이름이 아니라 `effect_id` 문자열)
2. 필터 프리셋의 **실제 파라미터 구조** (색온도·대비 등이 어떤 키로 저장되는가)
3. 텍스트 오버레이의 **폰트 이름 정확한 매칭** (한글 지원 폰트)
4. 버전별 호환성 (CapCut 4.x vs 5.x)

이 표는 **첫 추정치**이다. 실제 드래프트를 하나 만들어 CapCut 쪽에서 효과를 수동 적용하고 JSON 차이를 역공학해서 교정한다.
