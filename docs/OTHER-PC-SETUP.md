# 다른 PC 에서 sceneweaver-capcut 사용하기

이 문서는 이 repo 를 **처음** 자기 PC 에 clone / pull 받은 사용자를 위한 단계별 가이드다. CapCut 8.5.0 이상 데스크톱을 설치한 Windows 환경을 가정한다.

> **한 줄 요약**: 자산을 `workspace/ch{N}/{images, audio, subtitles}` 에 두고 → `python build_draft.py {N} && python inject_subtitles_v2.py {N} && python install_draft.py {N}` → CapCut 완전 종료 후 재실행 → 더블클릭 → 자동 배치된 영상·음성·자막 등장. 효과·BGM 만 수동 추가하면 끝.

> ⚠ **중요**: CapCut 을 설치하자마자는 안 됨. **한 번 실행해서 아무 프로젝트라도 저장** 한 뒤에야 드래프트 디렉터리가 생긴다 (§1-1).

---

## 1. 사전 준비 체크리스트

### 1-1. CapCut 첫 실행 (필수)

설치 직후엔 `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\` 폴더가 **존재하지 않는다**. 강제 생성:

1. CapCut 실행
2. "새 프로젝트" → 아무 이미지/영상 1개 드래그 → **"저장"** (이름 임의)
3. CapCut 종료 — X 버튼만으로는 부족. **작업관리자 (Ctrl+Shift+Esc) 에서 `CapCut.exe` 프로세스까지 모두 종료**

확인:

```powershell
explorer "$env:LOCALAPPDATA\CapCut\User Data\Projects\com.lveditor.draft"
```

이 폴더 안에 **`root_meta_info.json`** 과 방금 만든 프로젝트 폴더가 보여야 한다.

CapCut 릴리스별 경로 차이:
- 글로벌/한국 CapCut: `CapCut`
- 중국 내수 Jianying: `JianyingPro` — `%LOCALAPPDATA%` 전체에서 `com.lveditor.draft` 검색

### 1-2. Python + 이 repo

```bash
git clone https://github.com/leedonwoo2827-ship-it/sceneweaver-capcut
cd sceneweaver-capcut
python --version   # 3.9+
```

외부 의존성 없음 (표준 라이브러리만).

### 1-3. (선택) Claude Code 플러그인

`/weave-*` 슬래시 커맨드로 쓰려면 Claude Code 안에서:

```
/plugin marketplace add leedonwoo2827-ship-it/sceneweaver-capcut
/plugin install sceneweaver-capcut@sceneweaver-capcut
```

플러그인 없이 Python 명령 직접 호출도 가능.

---

## 2. 자산 준비

### 2-1. 폴더 구조

빌더가 기대하는 워크스페이스:

```
workspace/ch{NN}/
├── images/             ← *.jpeg / *.jpg / *.png
├── audio/              ← *.wav (이미지와 같은 개수)
└── subtitles/          ← (선택) *.srt
```

- 이미지·오디오 개수 일치 (정렬 순서로 1:1 페어링)
- 이미지: `ch02_01_*.jpeg`, `ch02_02_*.jpeg` … 정렬되면 OK
- 오디오: `01.wav`, `02.wav` … 또는 `ch02_01_narration.wav` … 정렬되면 OK
- 자막: `ch02_full.srt` 합본 또는 단일 SRT 1개 권장

### 2-2. ScriptForge 출력에서 옮기기

ScriptForge 가 만든 자산이 `<자산루트>\ch02\` 같은 외부 폴더에 있다면, 다음만 옮기면 됨:

```
<자산루트>\ch02\images\        →  workspace\ch02\images\
<자산루트>\ch02\audio\         →  workspace\ch02\audio\
<자산루트>\ch02\subtitles\     →  workspace\ch02\subtitles\
```

`scripts/`, `workspace/`, `tts/` 등 다른 폴더는 빌더가 안 씀 — 옮기실 필요 없음.

---

## 3. 한 줄 실행 (가장 일반적인 경우)

```bash
# 1. 자산 → 드래프트 폴더 (이미지/오디오만, 자막 없는 상태)
python skills/build-capcut-draft/build_draft.py 02

# 2. 자막 주입 (subtitles/*.srt 자동 탐지)
python skills/build-capcut-draft/inject_subtitles_v2.py 02

# 3. CapCut 디렉터리로 설치 + root_meta_info 갱신
python skills/build-capcut-draft/install_draft.py 02
```

각 단계 출력 예:

```
[info] 자산 페어 23개 스캔
[info] Resources/ 복사 완료, 합계 47,595,465 bytes
[info] draft_content.json 생성, draft_id=606E1F6B-..., 길이 594.332초
[ok] 빌드 완료: workspace/ch02/draft

[info] SRT cues parsed: 200
[ok] 자막 200개 주입 완료

[info] 폴더 복사 완료
[info] root_meta_info.json 백업: root_meta_info.json.bak.20260427_112126
[info] root_meta_info.json 갱신: all_draft_store 에 'ch02_draft_20260427' 추가
[ok] 설치 완료
```

이후:
1. **CapCut 완전 종료** (작업관리자에서 `CapCut.exe` 프로세스까지)
2. CapCut 재실행
3. 프로젝트 목록에서 `ch02_draft_{YYYYMMDD}` **더블클릭**
4. 자동 배치된 영상·음성·자막 확인
5. 효과·전환·BGM 만 수동 추가 → 렌더

---

## 4. 세부 제어 (선택)

### 4-1. 캔버스 / 폰트 / 폴더명

```bash
# 9:16 세로 영상
python skills/build-capcut-draft/build_draft.py 02 --canvas-w 1080 --canvas-h 1920

# 폰트 변경
python skills/build-capcut-draft/inject_subtitles_v2.py 02 --font "C:/Windows/Fonts/NanumGothic.ttf"

# 드래프트 폴더 이름 변경
python skills/build-capcut-draft/build_draft.py 02 --name ch02_v2_test

# 같은 이름 덮어쓰기 (재설치)
python skills/build-capcut-draft/install_draft.py 02 --overwrite
```

### 4-2. 자막 없이 빌드

`inject_subtitles_v2.py` 단계를 건너뛰면 자막 없는 드래프트가 됨. 자막은 CapCut UI 에서 수동 import 가능.

### 4-3. 명시적 SRT 지정

`subtitles/` 에 SRT 가 여러 개 있어 자동 탐지가 모호하면:

```bash
python skills/build-capcut-draft/inject_subtitles_v2.py \
  --draft workspace/ch02/draft \
  --srt workspace/ch02/subtitles/ch02_full.srt
```

---

## 5. 결과 확인

CapCut 에서 더블클릭했을 때 보여야 할 것:

- **비디오 트랙**: 이미지 N개가 순차 배치, 각 클립의 길이는 해당 오디오 길이와 동일
- **오디오 트랙**: wav N개가 순차 배치
- **자막 트랙** (자막 주입 시): 빨간 "A" 마커들. SRT 의 시각·텍스트가 정확히 반영
- **타임라인 총 길이**: 오디오 합과 일치

```
00:00 ─────────────────────────────────────────────  09:54
       │ ch02_01 │ ch02_02 │ ... │ ch02_23 │   ← 비디오
       │ 01.wav  │ 02.wav  │ ... │ 23.wav  │   ← 오디오
       │ 자막 큐 200개 (개별 짧은 막대)        │   ← 자막
```

---

## 6. 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| **`%LOCALAPPDATA%\CapCut\...` 경로 없음** | CapCut 첫 실행/저장 안 함 | §1-1 재수행 |
| **드래프트 목록에 안 보임** | `root_meta_info.json` 미갱신 (수동 폴더 복사한 경우) 또는 CapCut 캐시 | `install_draft.py` 사용. 또는 작업관리자에서 `CapCut.exe` 까지 종료 후 재시작 |
| **더블클릭해도 안 열림** | 자막을 v1 (`inject_subtitles.py`) 으로 주입함 | v2 (`inject_subtitles_v2.py`) 로 다시 → `install_draft.py 02 --overwrite` |
| **"비정상적인 경로" 에러** | `draft_fold_path` / `file_Path` 들이 실제 위치와 불일치 | `install_draft.py` 가 자동 갱신함. 수동 복사한 경우 발생 — `install_draft.py` 사용 권장 |
| **"미디어 없음" 표시** | `Resources/` 안의 파일이 사라졌거나 path 가 잘못됨 | `install_draft.py 02 --overwrite` 로 재설치 |
| **자막이 깨짐 / 안 나옴** | SRT 가 UTF-8 BOM + CRLF 가 아님 또는 v1 사용 | UTF-8 BOM 으로 재저장. v2 사용 확인 |
| **이미지 개수 ≠ 오디오 개수 에러** | `images/` 와 `audio/` 의 파일 개수가 다름 | 양쪽 동일하게 맞추기. 정렬 순서로 페어링됨 |
| **이전 드래프트가 사라짐** | CapCut UI 에서 폴더만 삭제 (root_meta 엔트리는 남음) | `python install_draft.py 02 --overwrite` 로 workspace 빌드 결과물 재설치 (자막까지 그대로 복원) |

---

## 7. 알려진 한계

- **전환·필터·BGM 은 수동**: 효과 자동 매핑은 v0.3 (추가 샘플 필요)
- **Mac 미검증**: Windows 우선. Mac 도 경로만 다르고 동작할 가능성 높지만 미테스트
- **CapCut 8.5.0 기준**: 더 새 버전에서 형식 바뀌면 재검증 필요. 깨질 시 정상 동작 샘플과 deep-diff
- **자막 스타일 customization**: 현재 v2 는 ch01 기준 default (검정 배경, alpha 0.5). 박스색/음영 변경은 CapCut UI 에서 수동 (사용자가 그렇게 쓰고 있음)

---

## 8. 동작 원리 (간단히)

내부에서 일어나는 일:

1. **`build_draft.py`** — 0421 정상 샘플 + ch01 정상 샘플의 형식을 그대로 따라 `draft_content.json` (타임라인) + `draft_meta_info.json` (메타) + 부속 파일 8개 + 빈 폴더 7개 생성. 자료 참조 패턴 (segment.extra_material_refs) 도 ch01 정상값 그대로.

2. **`inject_subtitles_v2.py`** — SRT 를 파싱해서 텍스트 트랙 + 자막 material 들을 생성. v1 이 깨진 5개 필드 (`check_flag=23`, `background_alpha=0.5`, `background_color="#000000"`, `background_style=1`, segment 의 `track_render_index=2`) 를 ch01 정상값으로 박아둠.

3. **`install_draft.py`** — `%LOCALAPPDATA%\CapCut\...\com.lveditor.draft\` 로 폴더 복사 + `draft_content.json` / `draft_meta_info.json` 의 path 필드들을 실제 설치 위치 기준으로 재작성 + `root_meta_info.json` 의 `all_draft_store[]` 에 새 엔트리 등록 (백업 자동 생성).

상세: [knowledge/capcut8-schema.md](../knowledge/capcut8-schema.md), [skills/build-capcut-draft/SKILL.md](../skills/build-capcut-draft/SKILL.md)

---

## 9. 관련 파일

- [skills/build-capcut-draft/build_draft.py](../skills/build-capcut-draft/build_draft.py)
- [skills/build-capcut-draft/inject_subtitles_v2.py](../skills/build-capcut-draft/inject_subtitles_v2.py)
- [skills/build-capcut-draft/install_draft.py](../skills/build-capcut-draft/install_draft.py)
- [skills/build-capcut-draft/templates/](../skills/build-capcut-draft/templates/) — 부속 파일 템플릿
- [skills/build-capcut-draft/SKILL.md](../skills/build-capcut-draft/SKILL.md) — 스크립트 명세
- [knowledge/capcut8-schema.md](../knowledge/capcut8-schema.md) — CapCut 8.x 스키마 분석
- [skills/build-capcut-draft/inject_subtitles.py](../skills/build-capcut-draft/inject_subtitles.py) — DEPRECATED v1 (참고용 보존)
