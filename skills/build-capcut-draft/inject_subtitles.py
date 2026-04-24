"""
sceneweaver-capcut v0.1.1 — 자막 트랙 자동 주입

기존 CapCut 8.x 드래프트 폴더의 draft_content.json 에 자막 트랙을
추가하고, draft_meta_info.json 의 draft_materials[type=2] 에
SRT 엔트리를 등록한다. SRT 규격: UTF-8 BOM + CRLF, 큐 시간은
HH:MM:SS,mmm → 초 → 마이크로초(μs) 변환.

스키마 출처: _assetst/0421-subs 샘플 (2026-04-21 diff).

사용:
    python inject_subtitles.py <draft_dir> <srt_path>

예:
    python inject_subtitles.py \
      "C:/Users/leedonwoo/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/ch01_draft_20260421" \
      "D:/cl150y/ch01/subtitles/ch01_full.srt"
"""

import json
import re
import shutil
import sys
import uuid
from pathlib import Path


def gen_uuid() -> str:
    """CapCut 샘플과 같은 대문자 혼합 UUID 포맷."""
    u = uuid.uuid4()
    return str(u).upper()[:18] + "-" + str(u).upper()[19:23].lower() + "-" + str(u).upper()[24:]


def parse_srt(path: Path) -> list[dict]:
    """SRT → [{start_us, duration_us, text}, ...]. 시간 단위 마이크로초."""
    raw = path.read_bytes().decode("utf-8-sig")
    # CRLF/LF 양쪽 허용
    blocks = re.split(r"\r?\n\r?\n+", raw.strip())
    cues = []
    ts_re = re.compile(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})")
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue
        # 첫 줄은 인덱스, 두번째는 타임스탬프
        m = ts_re.search(lines[1] if not ts_re.search(lines[0]) else lines[0])
        if not m:
            continue
        h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, m.groups())
        start_us = (h1 * 3600 + m1 * 60 + s1) * 1_000_000 + ms1 * 1000
        end_us = (h2 * 3600 + m2 * 60 + s2) * 1_000_000 + ms2 * 1000
        ts_idx = 0 if ts_re.search(lines[0]) else 1
        text = "\n".join(lines[ts_idx + 1 :]).strip()
        if not text:
            continue
        cues.append({"start_us": start_us, "duration_us": end_us - start_us, "text": text})
    return cues


def make_text_material(text_id: str, text: str, group_id: str, font_path: str) -> dict:
    """materials.texts 엔트리 생성. 샘플 0421-subs 기반."""
    content = json.dumps(
        {
            "styles": [
                {
                    "fill": {
                        "alpha": 1.0,
                        "content": {
                            "render_type": "solid",
                            "solid": {"alpha": 1.0, "color": [1.0, 1.0, 1.0]},
                        },
                    },
                    "font": {"id": "", "path": font_path},
                    "range": [0, len(text)],
                    "size": 5.0,
                }
            ],
            "text": text,
        },
        ensure_ascii=False,
    )
    return {
        "recognize_task_id": "",
        "id": text_id,
        "name": "",
        "recognize_text": "",
        "recognize_model": "",
        "punc_model": "",
        "type": "subtitle",
        "content": content,
        "base_content": "",
        "words": {"start_time": [], "end_time": [], "text": []},
        "current_words": {"start_time": [], "end_time": [], "text": []},
        "global_alpha": 1.0,
        "combo_info": {"text_templates": []},
        "caption_template_info": {
            "resource_id": "",
            "third_resource_id": "",
            "resource_name": "",
            "category_id": "",
            "category_name": "",
            "effect_id": "",
            "request_id": "",
            "path": "",
            "is_new": False,
            "source_platform": 0,
        },
        "layer_weight": 1,
        "letter_spacing": 0.0,
        "text_curve": None,
        "text_loop_on_path": False,
        "offset_on_path": 0.0,
        "enable_path_typesetting": False,
        "text_exceeds_path_process_type": 0,
        "text_typesetting_paths": None,
        "text_typesetting_paths_file": "",
        "text_typesetting_path_index": 0,
        "line_spacing": 0.02,
        "has_shadow": False,
        "shadow_color": "",
        "shadow_alpha": 0.9,
        "shadow_smoothing": 0.45,
        "shadow_distance": 5.0,
        "shadow_point": {"x": 0.6363961030678928, "y": -0.6363961030678928},
        "shadow_angle": -45.0,
        "shadow_thickness_projection_enable": False,
        "shadow_thickness_projection_angle": 0.0,
        "shadow_thickness_projection_distance": 0.0,
        "border_alpha": 1.0,
        "border_color": "",
        "border_width": 0.08,
        "border_mode": 0,
        "style_name": "",
        "text_color": "#FFFFFF",
        "text_alpha": 1.0,
        "font_name": "",
        "font_title": "none",
        "font_size": 5.0,
        "font_path": font_path,
        "font_id": "",
        "font_resource_id": "",
        "initial_scale": 1.0,
        "font_url": "",
        "typesetting": 0,
        "alignment": 1,
        "line_feed": 1,
        "use_effect_default_color": True,
        "is_rich_text": False,
        "shape_clip_x": False,
        "shape_clip_y": False,
        "ktv_color": "",
        "text_to_audio_ids": [],
        "bold_width": 0.0,
        "italic_degree": 0,
        "underline": False,
        "underline_width": 0.05,
        "underline_offset": 0.22,
        "sub_type": 0,
        "check_flag": 7,
        "text_size": 30,
        "font_category_name": "",
        "font_source_platform": 0,
        "font_third_resource_id": "",
        "font_category_id": "",
        "add_type": 2,
        "operation_type": 0,
        "recognize_type": 0,
        "fonts": [],
        "background_color": "",
        "background_alpha": 1.0,
        "background_style": 0,
        "background_round_radius": 0.0,
        "background_width": 0.14,
        "background_height": 0.14,
        "background_vertical_offset": 0.0,
        "background_horizontal_offset": 0.0,
        "background_fill": "",
        "single_char_bg_enable": False,
        "single_char_bg_color": "",
        "single_char_bg_alpha": 1.0,
        "single_char_bg_round_radius": 0.3,
        "single_char_bg_width": 0.0,
        "single_char_bg_height": 0.0,
        "single_char_bg_vertical_offset": 0.0,
        "single_char_bg_horizontal_offset": 0.0,
        "font_team_id": "",
        "tts_auto_update": False,
        "text_preset_resource_id": "",
        "group_id": group_id,
        "preset_id": "",
        "preset_name": "",
        "preset_category": "",
        "preset_category_id": "",
        "preset_index": 0,
        "preset_has_set_alignment": False,
        "force_apply_line_max_width": False,
        "language": "",
        "relevance_segment": [],
        "original_size": [],
        "fixed_width": -1.0,
        "fixed_height": -1.0,
        "line_max_width": 0.82,
        "oneline_cutoff": False,
        "cutoff_postfix": "",
        "subtitle_template_original_fontsize": 0.0,
        "subtitle_keywords": None,
        "inner_padding": -1.0,
        "multi_language_current": "none",
        "source_from": "",
        "is_lyric_effect": False,
        "lyric_group_id": "",
        "lyrics_template": {
            "resource_id": "",
            "resource_name": "",
            "panel": "",
            "effect_id": "",
            "path": "",
            "category_id": "",
            "category_name": "",
            "request_id": "",
        },
        "is_batch_replace": False,
        "is_words_linear": False,
        "ssml_content": "",
        "subtitle_keywords_config": None,
        "sub_template_id": -1,
        "translate_original_text": "",
    }


def make_animation(anim_id: str) -> dict:
    return {
        "id": anim_id,
        "type": "sticker_animation",
        "animations": [],
        "multi_language_current": "none",
    }


def make_segment(seg_id: str, text_id: str, anim_id: str, start_us: int, duration_us: int, render_index: int) -> dict:
    return {
        "id": seg_id,
        "source_timerange": None,
        "target_timerange": {"start": start_us, "duration": duration_us},
        "render_timerange": {"start": 0, "duration": 0},
        "desc": "",
        "state": 0,
        "speed": 1.0,
        "is_loop": False,
        "is_tone_modify": False,
        "reverse": False,
        "intensifies_audio": False,
        "cartoon": False,
        "volume": 1.0,
        "last_nonzero_volume": 1.0,
        "clip": {
            "scale": {"x": 1.0, "y": 1.0},
            "rotation": 0.0,
            "transform": {"x": 0.0, "y": -0.8},
            "flip": {"vertical": False, "horizontal": False},
            "alpha": 1.0,
        },
        "uniform_scale": {"on": True, "value": 1.0},
        "material_id": text_id,
        "extra_material_refs": [anim_id],
        "render_index": render_index,
        "keyframe_refs": [],
        "enable_lut": False,
        "enable_adjust": False,
        "enable_hsl": False,
        "visible": True,
        "group_id": "",
        "enable_color_curves": True,
        "enable_hsl_curves": True,
        "track_render_index": 1,
        "hdr_settings": None,
        "enable_color_wheels": True,
        "track_attribute": 0,
        "is_placeholder": False,
        "template_id": "",
        "enable_smart_color_adjust": False,
        "template_scene": "default",
        "common_keyframes": [],
        "caption_info": None,
        "responsive_layout": {
            "enable": False,
            "target_follow": "",
            "size_layout": 0,
            "horizontal_pos_layout": 0,
            "vertical_pos_layout": 0,
        },
        "enable_color_match_adjust": False,
        "enable_color_correct_adjust": False,
        "enable_adjust_mask": False,
        "raw_segment_id": "",
        "lyric_keyframes": None,
        "enable_video_mask": True,
        "digital_human_template_group_id": "",
        "color_correct_alg_result": "",
        "source": "segmentsourcenormal",
        "enable_mask_stroke": False,
        "enable_mask_shadow": False,
        "enable_color_adjust_pro": False,
    }


def inject(draft_dir: Path, srt_path: Path, font_path: str = "C:/Windows/Fonts/malgun.ttf") -> int:
    content_path = draft_dir / "draft_content.json"
    meta_path = draft_dir / "draft_meta_info.json"

    # 백업
    shutil.copy2(content_path, content_path.with_suffix(".json.bak_before_subs"))
    shutil.copy2(meta_path, meta_path.with_suffix(".json.bak_before_subs"))

    # 파싱
    cues = parse_srt(srt_path)
    print(f"[info] SRT cues parsed: {len(cues)}")

    # draft_content.json 수정
    with content_path.open(encoding="utf-8") as f:
        content = json.load(f)

    # 기존 text 트랙 제거 (재실행 안전성)
    content["tracks"] = [t for t in content["tracks"] if t.get("type") != "text"]

    # materials.texts / animations 에서 기존 subtitle 항목 제거
    content["materials"].setdefault("texts", [])
    content["materials"]["texts"] = [
        t for t in content["materials"]["texts"] if t.get("type") != "subtitle"
    ]
    content["materials"].setdefault("material_animations", [])
    # material_animations 는 자막 외에도 쓰일 수 있어 보존; 대신 ID 충돌 없게 관리

    group_id = f"sceneweaver_subs_{int(cues[0]['start_us']) if cues else 0}"
    text_track_id = gen_uuid()
    segments = []
    for i, cue in enumerate(cues):
        text_id = gen_uuid()
        anim_id = gen_uuid()
        seg_id = gen_uuid()
        content["materials"]["texts"].append(
            make_text_material(text_id, cue["text"], group_id, font_path)
        )
        content["materials"]["material_animations"].append(make_animation(anim_id))
        segments.append(
            make_segment(seg_id, text_id, anim_id, cue["start_us"], cue["duration_us"], 14000 + i)
        )

    content["tracks"].append(
        {
            "id": text_track_id,
            "type": "text",
            "segments": segments,
            "flag": 1,
            "attribute": 0,
            "name": "",
            "is_default_name": True,
        }
    )

    with content_path.open("w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, separators=(",", ":"))

    # draft_meta_info.json 수정
    with meta_path.open(encoding="utf-8") as f:
        meta = json.load(f)

    srt_name = srt_path.name
    resources_srt = str(draft_dir / "Resources" / srt_name).replace("\\", "/")
    srt_entry = {
        "ai_group_type": "",
        "create_time": 0,
        "duration": 0,
        "enter_from": 0,
        "extra_info": srt_name,
        "file_Path": resources_srt,
        "height": 0,
        "id": str(uuid.uuid4()),
        "import_time": 0,
        "import_time_ms": 0,
        "item_source": 1,
        "md5": "",
        "metetype": "none",
        "roughcut_time_range": {"duration": 0, "start": -1},
        "sub_time_range": {"duration": -1, "start": -1},
        "type": 0,
        "width": 0,
    }
    # type=2 버킷 찾기/생성
    buckets = {b["type"]: b for b in meta.get("draft_materials", [])}
    if 2 not in buckets:
        meta.setdefault("draft_materials", []).append({"type": 2, "value": []})
        buckets = {b["type"]: b for b in meta["draft_materials"]}
    bucket2 = buckets[2]
    # 중복 방지: 동일 extra_info 제거 후 재등록
    bucket2["value"] = [v for v in bucket2.get("value", []) if v.get("extra_info") != srt_name]
    bucket2["value"].append(srt_entry)

    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, separators=(",", ":"))

    return len(cues)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: python inject_subtitles.py <draft_dir> <srt_path> [font_path]")
        sys.exit(2)
    draft_dir = Path(sys.argv[1])
    srt_path = Path(sys.argv[2])
    font_path = sys.argv[3] if len(sys.argv) > 3 else "C:/Windows/Fonts/malgun.ttf"
    n = inject(draft_dir, srt_path, font_path)
    print(f"[ok] injected {n} subtitle cues into {draft_dir}")
