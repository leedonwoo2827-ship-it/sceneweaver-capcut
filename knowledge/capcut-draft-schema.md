# CapCut 드래프트 스키마 — 4.x 레거시 기록

> **⚠ 이 문서는 CapCut 4.x 가정의 역사적 기록입니다.** 이전 sceneweaver 프로젝트(v0.2)가 참고하던 버전이며, **CapCut 8.x에서는 구조가 크게 달라졌다**. 4.x 가정으로 빌드된 드래프트는 CapCut 8.5.0에서 "비정상적인 경로" 에러로 열리지 않는다.
>
> v8.x 실제 구조는 [capcut8-schema.md](capcut8-schema.md) 참고. 이 레거시 문서는 v4.x → v8.x 변경점을 파악할 때 **diff 기준**으로만 활용.

## 드래프트 폴더 구조

```
com.lveditor.draft/
└── {draft_name}_{uuid}/
    ├── draft_info.json          # 타임라인 본체
    ├── draft_meta_info.json     # 드래프트 목록에 표시되는 메타
    ├── draft_cover.jpg          # 썸네일 (선택)
    └── materials/               # 미디어 원본 사본
        ├── {file}.png
        ├── {file}.mp3
        └── {file}.srt
```

CapCut 드래프트 디렉터리 위치:
- Windows: `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\`
- Mac: `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/`

## draft_info.json 최상위 구조 (개요)

```jsonc
{
  "canvas_config": {
    "width": 1920,
    "height": 1080,
    "ratio": "16:9"
  },
  "duration": 120000000,              // 전체 길이, 마이크로초(μs)
  "fps": 30,
  "materials": {
    "videos": [ /* 이미지/영상 재료 */ ],
    "audios": [ /* 오디오 재료 */ ],
    "texts":  [ /* 텍스트/자막 재료 */ ],
    "stickers": [],
    "effects": [],
    "transitions": [ /* 전환 효과 인스턴스 */ ]
  },
  "tracks": [
    { "type": "video",    "segments": [ /* ... */ ] },
    { "type": "audio",    "segments": [ /* ... */ ] },
    { "type": "text",     "segments": [ /* 자막 */ ] }
  ],
  "platform": "windows",
  "version": 360000
}
```

## 시간 단위

- **모든 시간은 마이크로초(μs, 10^-6초)**
- 변환: `μs = 초 × 1_000_000`
- 예: 2.5초 → `2500000`

## materials 섹션

각 재료는 고유 UUID를 가진다. 트랙 세그먼트는 이 UUID로 참조한다.

### videos (이미지 포함)

```jsonc
{
  "id": "uuid-v4-string",
  "type": "photo",                   // 정지 이미지
  "path": "materials/ch03_01_1953_classroom.png",
  "width": 1920,
  "height": 1080,
  "duration": 0                      // 이미지는 0, 트랙에서 길이 결정
}
```

### audios

```jsonc
{
  "id": "uuid-v4-string",
  "type": "extract_music",
  "path": "materials/ch03_01_narration.mp3",
  "duration": 25000000
}
```

### texts (자막)

```jsonc
{
  "id": "uuid-v4-string",
  "type": "text",
  "content": "1953년 하버드, 심리학 교수 스키너는",
  "font": "思源黑体",                 // 한글 폰트 변경 필요
  "font_size": 48,
  "color": "#FFFFFF",
  "stroke_color": "#000000",
  "stroke_width": 2
}
```

### transitions

`scene_meta.transition_hint` → CapCut 전환 매핑은 `transition-library.md` 참조.

## tracks 섹션

### 비디오 트랙

```jsonc
{
  "type": "video",
  "segments": [
    {
      "material_id": "uuid-of-image",
      "target_timerange": {
        "start": 0,
        "duration": 25000000       // 씬 1의 narration_seconds
      },
      "source_timerange": {
        "start": 0,
        "duration": 25000000
      },
      "clip": {
        "scale": { "x": 1.0, "y": 1.0 },
        "transform": { "x": 0, "y": 0 }
      }
    },
    {
      "material_id": "uuid-of-image-2",
      "target_timerange": { "start": 25000000, "duration": 20000000 }
    }
  ]
}
```

### 자막 트랙

SRT 각 큐를 세그먼트로 변환:

```jsonc
{
  "type": "text",
  "segments": [
    {
      "material_id": "uuid-of-text",
      "target_timerange": {
        "start": 1500000,          // SRT 00:00:01,500
        "duration": 3000000        // 3.0초 지속
      },
      "clip": {
        "transform": { "x": 0, "y": -400 }   // 화면 하단
      }
    }
  ]
}
```

## draft_meta_info.json

```jsonc
{
  "draft_id": "uuid-v4-string",
  "draft_name": "ch03_draft_20260415",
  "tm_draft_create": 1744684800000000,   // 마이크로초 타임스탬프
  "tm_draft_modified": 1744684800000000,
  "cover": "draft_cover.jpg",
  "duration": 120000000
}
```

## 차기 세션에서 확인해야 할 사항 (TODO)

아래 항목은 **Claude Code 코웍 세션에서 실제 CapCut 드래프트를 하나 만들어보고 그 JSON을 읽어** 교정해야 한다:

1. 실제 draft_info.json 최상위 필드 이름의 정확한 철자 (snake_case/camelCase 혼재 가능)
2. 한글 폰트 기본값 (CapCut 내장 한글 폰트 목록)
3. 전환 효과의 정확한 ID 문자열 (예: `fade_in` → 실제 내부 값)
4. 자막 스타일 프리셋 (`text_style_id` 등)
5. BGM 트랙을 "빈 슬롯"으로 만드는 방법 (또는 placeholder 트랙)
6. `version` 값이 CapCut 버전별로 어떻게 다른가

## 참고

- 본 문서는 **의도적으로 개요 수준**으로 둔다. 상세 매핑은 실제 CapCut으로 드래프트를 하나 만들어 열어본 뒤 채운다.
- CapCut의 드래프트 포맷은 버전에 따라 변동성이 크다. `build-capcut-draft` 스킬은 버전 감지 로직을 가져야 한다.
