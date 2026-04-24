# 다른 PC 에서 sceneweaver-capcut 사용하기

이 문서는 이 repo 를 **처음** 자기 PC 에 clone / pull 받은 사용자를 위한 세팅 가이드다. CapCut 8.5.0 이상 데스크톱을 설치한 Windows 환경을 가정한다.

> 한 줄 요약: CapCut 을 **한 번 열어서 아무 프로젝트라도 저장** 한 뒤에야 드래프트 디렉터리가 생긴다. 드래프트 폴더만 복사해서는 CapCut 목록에 **뜨지 않는다** — 전역 레지스트리(`root_meta_info.json`) 에 엔트리를 추가해야 한다.

---

## 1. 사전 준비

### 1-1. CapCut 첫 실행 (필수)

설치 직후에는 `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\` 폴더 자체가 **존재하지 않는다**. 다음 단계로 강제 생성한다:

1. CapCut 실행
2. "새 프로젝트" → 아무 이미지/영상 1개 드래그 → "저장" (프로젝트 이름 임의)
3. CapCut 종료 (X 버튼만으로는 부족 — 작업관리자에서 `CapCut.exe` 프로세스까지 모두 종료)

확인:

```powershell
explorer "%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft"
```

이 폴더 안에 **`root_meta_info.json`** 파일과 방금 만든 프로젝트 폴더가 보여야 한다. 없으면 CapCut 버전/릴리스가 달라 경로가 다를 수 있다:
- 글로벌/한국 CapCut: `CapCut`
- 중국 내수 Jianying: `JianyingPro` — 폴더 이름이 다름. `%LOCALAPPDATA%` 전체에서 `com.lveditor.draft` 문자열로 검색

### 1-2. Python + 이 repo

```bash
git clone https://github.com/leedonwoo2827-ship-it/sceneweaver-capcut
cd sceneweaver-capcut
python --version   # 3.9+ 권장
```

### 1-3. Claude Code 플러그인 (선택)

Claude Code 환경에서 `/weave-*` 슬래시 커맨드로 쓰려면:

```
/plugin marketplace add leedonwoo2827-ship-it/sceneweaver-capcut
/plugin install sceneweaver-capcut@sceneweaver-capcut
```

플러그인 없이 수동으로도 전부 가능.

---

## 2. 작업 흐름 선택

현재(v0.1.1) 세 가지 경로가 있다. **A안** 이 가장 확실하고, **B안** 은 Claude 와 반자동, **C안** 은 지금 시점엔 비권장.

### A안 — CapCut 안에서 수동 조립 (15분, 100% 동작)

자동화 없이 CapCut UI 만으로 조립. 자산이 이미 챕터 폴더에 모여 있으면 가장 빠름.

1. CapCut → 새 프로젝트
2. 미디어 패널 → "폴더 가져오기" → 이미지 폴더 선택 (전체 임포트)
3. 미디어 패널 → "폴더 가져오기" → 오디오 폴더 선택
4. 이미지들 Shift 전체 선택 → 비디오 트랙 1 에 드래그 (순차 배치)
5. 오디오들 전체 선택 → 오디오 트랙 1 에 드래그
6. 각 이미지 클립 우클릭 → "재생 시간에 맞춤" 으로 해당 오디오 길이에 스냅
7. 자막 패널 → "가져오기" → SRT 파일 로드

**언제 이걸 쓰나**: 지금 영상을 완성해야 할 때, Claude 자동화를 기다릴 수 없을 때.

### B안 — Claude 와 반자동 (ch01 재현 방식, 30-45분)

이 repo 의 `/weave-*` 파이프라인을 쓰되, 드래프트 조립은 Claude 가 샘플 기반으로 직접 수행.

**준비**: 상류 자산을 한 폴더에 모아둔다 (예: `D:\video-src\ch02\`):
```
D:\video-src\ch02\
├── script\ch02_script.json       # ScriptForge 출력
├── images\ch02_01_*.jpeg         # FlowGenie 출력
│   ├── ...
│   └── ch02_20_*.jpeg
└── audio\01.wav                  # TTS 출력 (또는 ch02_01_narration.wav)
    ├── ...
    └── 20.wav
```

**실행**:

```
/weave-ingest 2 --script-path D:\video-src\ch02\script\ch02_script.json \
                --images-dir D:\video-src\ch02\images \
                --audio-dir D:\video-src\ch02\audio
```

→ `workspace/ch02/` 에 정규화된 자산 생성.

```
/weave-subtitle 2
```

→ `workspace/ch02/subtitles/ch02_full.srt` 생성. **에디터로 열어서** 타이밍/줄바꿈 손보고 저장 (UTF-8 BOM + CRLF 유지). 기본 생성 규칙: 한 줄 18자, 두 줄까지, 한 큐 36자 이하.

**드래프트 조립** — 여기서 Claude 에게 다음처럼 지시:

> "workspace/ch02 자산으로 CapCut 8.5.0 드래프트를 조립해줘. _assetst/0421 샘플의 draft_content.json / draft_meta_info.json 을 템플릿으로 사용하고, 2026-04-21 에 ch01 로 성공한 방식을 그대로 따라. 이미지 20장 + 오디오 20개 + SRT 1개."

Claude 가 생성하는 것:
- `workspace/ch02/draft/draft_content.json` — 타임라인 본체 (tracks, materials, canvas)
- `workspace/ch02/draft/draft_meta_info.json` — UUID, 이름, `draft_materials` 3개 버킷(이미지 0, 오디오 0, 자막 2)
- `workspace/ch02/draft/draft_cover.jpg`, 기타 부속 파일
- `workspace/ch02/draft/Resources/` 에 자산 사본

**설치 — 수동 복사**:

```powershell
$SRC = "D:\00work\260417-sceneweaver-capcut\workspace\ch02\draft"
$DST = "$env:LOCALAPPDATA\CapCut\User Data\Projects\com.lveditor.draft\ch02_draft_20260424"
Copy-Item -Path $SRC -Destination $DST -Recurse
```

폴더 이름은 `ch{NN}_draft_{YYYYMMDD}` 권장. 이 이름은 `draft_meta_info.json` 의 `draft_name` 과 **일치해야** 한다 (Claude 가 조립 시 같이 맞춤).

**중요 — `root_meta_info.json` 에 엔트리 추가**:

`com.lveditor.draft\root_meta_info.json` 을 연다. `all_draft_store` 배열이 있다. 기존 엔트리 하나를 복사해서 새 드래프트용으로 수정:

```json
{
  "draft_cover": "C:\\Users\\<you>\\AppData\\Local\\CapCut\\User Data\\Projects\\com.lveditor.draft\\ch02_draft_20260424\\draft_cover.jpg",
  "draft_fold_path": "C:\\Users\\<you>\\AppData\\Local\\CapCut\\User Data\\Projects\\com.lveditor.draft\\ch02_draft_20260424",
  "draft_id": "<draft_meta_info.json 의 draft_id 와 동일 UUID>",
  "draft_name": "ch02_draft_20260424",
  "tm_draft_create": <현재시각 Unix ms>,
  "tm_draft_modified": <현재시각 Unix ms>,
  "...": "나머지 필드는 기존 엔트리에서 그대로 복제"
}
```

저장 전 반드시 백업: `Copy-Item root_meta_info.json root_meta_info.json.bak`

**자막 주입**:

```bash
python skills/build-capcut-draft/inject_subtitles.py \
  "%LOCALAPPDATA%/CapCut/User Data/Projects/com.lveditor.draft/ch02_draft_20260424" \
  "workspace/ch02/subtitles/ch02_full.srt"
```

**CapCut 재시작**: 트레이/작업관리자 프로세스까지 모두 종료 후 다시 실행. 드래프트 목록에 `ch02_draft_20260424` 가 보이고, 클릭하면 타임라인이 뜬다.

### C안 — 자동화 빌더 (v0.2 대기)

`/weave-draft 2 --install` 이 end-to-end 로 동작하게 만드는 작업은 v0.2 TODO. 아직 스크립트가 없다. 지금은 B안으로.

---

## 3. 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| 드래프트 폴더 복사했는데 CapCut 목록에 안 뜸 | `root_meta_info.json` 의 `all_draft_store` 에 엔트리 없음 | 위 B안 "중요" 섹션 대로 엔트리 추가 후 CapCut 완전 재시작 |
| "비정상적인 경로" 에러 | `draft_meta_info.json` 의 `draft_fold_path`/`draft_root_path` 가 실제 위치와 불일치 | 복사 후 실제 경로로 문자열 치환 |
| "미디어 없음" 표시 | `draft_materials[].file_Path` 의 절대경로에 파일이 없음 | 자산을 `<드래프트>/Resources/` 아래로 옮기고 `file_Path` 를 해당 경로로 재작성 |
| 자막이 깨짐 | SRT 가 UTF-8 BOM + CRLF 가 아님 | 에디터에서 인코딩/개행 설정 후 재저장 |
| `%LOCALAPPDATA%\CapCut\...` 경로가 없음 | CapCut 첫 실행/저장 안 함 | §1-1 단계 재수행 |
| Claude 가 "v0.1 스텁이라 아무것도 없다" 라고 답함 | 오래된 문서만 보고 판단함 | `git pull` 후 [knowledge/capcut8-schema.md](../knowledge/capcut8-schema.md) 와 [skills/build-capcut-draft/SKILL.md](../skills/build-capcut-draft/SKILL.md) 최신 상태 확인 요청 |

---

## 4. 관련 레퍼런스

- [knowledge/capcut8-schema.md](../knowledge/capcut8-schema.md) — v4.x → v8.x 차이, 실제 필드 관찰
- [knowledge/capcut-draft-schema.md](../knowledge/capcut-draft-schema.md) — 레거시 v4.x 참고용
- [knowledge/subtitle-style-guide.md](../knowledge/subtitle-style-guide.md) — SRT 생성 규칙
- [_assetst/0421/](../_assetst/0421/) — CapCut 8.5.0 에서 저장한 최소 드래프트 샘플
- [skills/build-capcut-draft/inject_subtitles.py](../skills/build-capcut-draft/inject_subtitles.py) — 자막 트랙 주입기
