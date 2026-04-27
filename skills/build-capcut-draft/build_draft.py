"""
sceneweaver-capcut v0.2.0 - 자동 빌더

workspace/ch{NN}/{images/, audio/} → workspace/ch{NN}/draft/
CapCut 8.x 가 직접 열 수 있는 드래프트 폴더 자동 생성.

기준 모델: _assetst/0421/ + ch01_draft_20260421/ (CapCut 8.5.0 정상 로드 검증됨)
자막은 inject_subtitles_v2.py 가 별도로 처리.

사용:
    python build_draft.py 02
    python build_draft.py 02 --workspace D:\\custom\\ws

검증:
    이 PC 의 ch01 (정상 동작) draft_content.json 의 자료 참조 패턴을 그대로 따름.
    - video segment.extra_material_refs (7개): speeds + placeholder_infos + canvases
      + sound_channel_mappings + material_colors + loudnesses + vocal_separations
    - audio segment.extra_material_refs (5개): speeds + placeholder_infos + beats
      + sound_channel_mappings + vocal_separations
"""

import argparse
import json
import shutil
import struct
import sys
import time
import uuid
import wave
from pathlib import Path

# ─── 상수 ──────────────────────────────────────────────
CAPCUT_APP_ID = 3704
CAPCUT_APP_VERSION = "8.5.0"
CAPCUT_OS = "windows"
CAPCUT_OS_VERSION = "10.0.19045"
DEFAULT_FPS = 30
DEFAULT_CANVAS_W = 1920
DEFAULT_CANVAS_H = 1080
PHOTO_DEFAULT_DURATION_US = 10_800_000_000  # CapCut 의 photo material default

TEMPLATE_DIR = Path(__file__).parent / "templates"


# ─── 헬퍼 ──────────────────────────────────────────────
def gen_uuid() -> str:
    """CapCut 형식 UUID — 표준 36자리 (8-4-4-4-12), 4번째 그룹만 소문자.

    예: "5F082F9C-B126-4182-a8a1-BD0959E8F724"
    UUID 위치: pos 0-7 / 8 / 9-12 / 13 / 14-17 / 18 / 19-22 / 23 / 24-35
    """
    u = str(uuid.uuid4()).upper()
    return u[:19] + u[19:23].lower() + u[23:]  # 4번째 그룹 (pos 19-22) 만 소문자


def now_us() -> int:
    """현재 Unix 시각을 마이크로초 16자리 정수로."""
    return int(time.time() * 1_000_000)


def wav_duration_us(path: Path) -> int:
    """WAV 파일 길이 (마이크로초)."""
    with wave.open(str(path), "rb") as w:
        return int(w.getnframes() * 1_000_000 / w.getframerate())


def jpeg_size(path: Path) -> tuple[int, int]:
    """JPEG width/height 추출 (PIL 의존성 없이)."""
    with open(path, "rb") as f:
        if f.read(2) != b"\xff\xd8":
            return DEFAULT_CANVAS_W, DEFAULT_CANVAS_H  # fallback
        while True:
            chunk = f.read(2)
            if len(chunk) < 2:
                return DEFAULT_CANVAS_W, DEFAULT_CANVAS_H
            marker = struct.unpack(">H", chunk)[0]
            if 0xFFC0 <= marker <= 0xFFCF and marker not in (0xFFC4, 0xFFC8, 0xFFCC):
                f.read(3)  # length(2) + precision(1)
                h, w = struct.unpack(">HH", f.read(4))
                return w, h
            seg_len = struct.unpack(">H", f.read(2))[0]
            f.seek(seg_len - 2, 1)


def image_size(path: Path) -> tuple[int, int]:
    """이미지 크기 추출. JPEG 만 정확. PNG 등은 fallback."""
    if path.suffix.lower() in (".jpg", ".jpeg"):
        return jpeg_size(path)
    return DEFAULT_CANVAS_W, DEFAULT_CANVAS_H  # PNG 등은 default


# ─── 자료 (material) 생성 함수 ─────────────────────────
def make_video_material(image_path_in_resources: str, name: str, w: int, h: int) -> dict:
    return {
        "aigc_history_id": "", "aigc_item_id": "", "aigc_type": "none",
        "audio_fade": None,
        "beauty_body_auto_preset": None, "beauty_body_preset_id": "",
        "beauty_face_auto_preset": {"name": "", "preset_id": "", "rate_map": "", "scene": ""},
        "beauty_face_auto_preset_infos": [], "beauty_face_preset_infos": [],
        "cartoon_path": "", "category_id": "", "category_name": "local",
        "check_flag": 62978047, "content_feature_info": None, "corner_pin": None,
        "crop": {"lower_left_x": 0.0, "lower_left_y": 1.0, "lower_right_x": 1.0, "lower_right_y": 1.0,
                 "upper_left_x": 0.0, "upper_left_y": 0.0, "upper_right_x": 1.0, "upper_right_y": 0.0},
        "crop_ratio": "free", "crop_scale": 1.0,
        "duration": PHOTO_DEFAULT_DURATION_US, "extra_type_option": 0,
        "formula_id": "", "freeze": None,
        "has_audio": False, "has_sound_separated": False,
        "height": h, "id": gen_uuid(),
        "intensifies_audio_path": "", "intensifies_path": "",
        "is_ai_generate_content": False, "is_copyright": False,
        "is_text_edit_overdub": False, "is_unified_beauty_mode": False,
        "live_photo_cover_path": "", "live_photo_timestamp": -1,
        "local_id": "", "local_material_from": "",
        "local_material_id": str(uuid.uuid4()),
        "material_id": "", "material_name": name, "material_url": "",
        "matting": {"custom_matting_id": "", "enable_matting_stroke": False, "expansion": 0,
                    "feather": 0, "flag": 0, "has_use_quick_brush": False,
                    "has_use_quick_eraser": False, "interactiveTime": [],
                    "path": "", "reverse": False, "strokes": []},
        "media_path": "", "multi_camera_info": None, "object_locked": None,
        "origin_material_id": "", "path": image_path_in_resources,
        "picture_from": "none", "picture_set_category_id": "", "picture_set_category_name": "",
        "request_id": "", "reverse_intensifies_path": "", "reverse_path": "",
        "smart_match_info": "", "smart_motion": None, "source": 0, "source_platform": 0,
        "stable": {"matrix_path": "", "stable_level": 0,
                   "time_range": {"duration": 0, "start": 0}},
        "team_id": "", "type": "photo",
        "video_algorithm": {"algorithms": [], "complement_frame_config": None, "deflicker": None,
                            "gameplay_configs": [], "motion_blur_config": None,
                            "mouth_shape_driver": None, "noise_reduction": None, "path": "",
                            "quality_enhance": None, "smart_complement_frame": None,
                            "smart_motion_config": None, "super_resolution": None,
                            "time_range": None},
        "width": w,
        "audio_loudnesses": [], "background_blur": -1.0,
        "is_smart_motion": False, "smart_motion_id": "",
        "live_photo_image_path": "",
    }


def make_audio_material(audio_path_in_resources: str, name: str, duration_us: int) -> dict:
    return {
        "app_id": 0, "category_id": "", "category_name": "local",
        "check_flag": 1, "copyright_limit_type": "none",
        "duration": duration_us, "effect_id": "", "formula_id": "",
        "id": gen_uuid(),
        "intensifies_path": "", "is_ai_clone_tone": False,
        "is_text_edit_overdub": False, "is_ugc": False,
        "local_material_id": "", "music_id": "",
        "name": name, "path": audio_path_in_resources,
        "query": "", "request_id": "", "resource_id": "",
        "search_id": "", "source_from": "", "source_platform": 0, "team_id": "",
        "text_id": "", "tone_category_id": "", "tone_category_name": "",
        "tone_effect_id": "", "tone_effect_name": "", "tone_platform": "",
        "tone_second_category_id": "", "tone_second_category_name": "",
        "tone_speaker": "", "tone_type": "", "type": "extract_music",
        "video_id": "", "wave_points": [],
    }


def make_canvas() -> dict:
    return {"id": gen_uuid(), "type": "canvas_color", "color": "", "image": "",
            "image_id": "", "image_name": "", "album_image": "", "blur": 0.0,
            "source_platform": 0, "team_id": "", "size": 0.0}


def make_speed() -> dict:
    return {"id": gen_uuid(), "mode": 0, "speed": 1.0, "curve_speed": None}


def make_sound_channel_mapping() -> dict:
    return {"id": gen_uuid(), "audio_channel_mapping": 0,
            "is_config_open": False, "type": ""}


def make_vocal_separation() -> dict:
    return {"id": gen_uuid(), "choice": 0, "production_path": "",
            "removed_sounds": [], "time_range": None, "type": "vocal_separation"}


def make_placeholder_info() -> dict:
    return {"error_path": "", "error_text": "", "id": gen_uuid(),
            "meta_type": "none", "res_path": "", "res_text": "",
            "type": "placeholder_info"}


def make_material_color() -> dict:
    return {"id": gen_uuid(), "is_color_clip": False, "is_gradient": False,
            "solid_color": "", "gradient_colors": [], "gradient_percents": [],
            "gradient_angle": 90.0, "width": 0.0, "height": 0.0}


def make_loudness() -> dict:
    return {"enable": False, "file_id": "", "id": gen_uuid(),
            "loudness_param": None, "target_loudness": 0.0, "time_range": None}


def make_beat() -> dict:
    return {"ai_beats": {"melody_path": "", "ai_beats_path": "", "beats_path": ""},
            "enable_ai_beats": False, "gear": 404, "gear_count": 0,
            "id": gen_uuid(), "mode": 404, "type": "beats",
            "user_beats": [], "user_delete_ai_beats": None}


def make_video_segment(material_id: str, refs: dict, target_start_us: int, duration_us: int,
                       render_index: int) -> dict:
    """이미지 segment. refs 는 {speeds, placeholder_infos, canvases, sound_channel_mappings,
    material_colors, loudnesses, vocal_separations} ID 들."""
    return {
        "id": gen_uuid(),
        "material_id": material_id,
        "extra_material_refs": [
            refs["speeds"], refs["placeholder_infos"], refs["canvases"],
            refs["sound_channel_mappings"], refs["material_colors"],
            refs["loudnesses"], refs["vocal_separations"],
        ],
        "source_timerange": {"start": 0, "duration": duration_us},
        "target_timerange": {"start": target_start_us, "duration": duration_us},
        "render_timerange": {"start": 0, "duration": 0},
        "desc": "", "state": 0, "speed": 1.0,
        "is_loop": False, "is_tone_modify": False, "reverse": False,
        "intensifies_audio": False, "cartoon": False,
        "volume": 1.0, "last_nonzero_volume": 1.0,
        "clip": {"scale": {"x": 1.0, "y": 1.0}, "rotation": 0.0,
                 "transform": {"x": 0.0, "y": 0.0},
                 "flip": {"vertical": False, "horizontal": False}, "alpha": 1.0},
        "uniform_scale": {"on": True, "value": 1.0},
        "render_index": render_index,
        "keyframe_refs": [],
        "enable_lut": False, "enable_adjust": False, "enable_hsl": False,
        "visible": True, "group_id": "",
        "enable_color_curves": True, "enable_hsl_curves": True,
        "track_render_index": 0, "hdr_settings": None,
        "enable_color_wheels": True, "track_attribute": 0,
        "is_placeholder": False, "template_id": "",
        "enable_smart_color_adjust": False, "template_scene": "default",
        "common_keyframes": [], "caption_info": None,
        "responsive_layout": {"enable": False, "target_follow": "", "size_layout": 0,
                              "horizontal_pos_layout": 0, "vertical_pos_layout": 0},
        "enable_color_match_adjust": False, "enable_color_correct_adjust": False,
        "enable_adjust_mask": False, "raw_segment_id": "", "lyric_keyframes": None,
        "enable_video_mask": True, "digital_human_template_group_id": "",
        "color_correct_alg_result": "", "source": "segmentsourcenormal",
        "enable_mask_stroke": False, "enable_mask_shadow": False,
        "enable_color_adjust_pro": False,
    }


def make_audio_segment(material_id: str, refs: dict, target_start_us: int,
                       duration_us: int, render_index: int) -> dict:
    """오디오 segment. refs 는 {speeds, placeholder_infos, beats, sound_channel_mappings,
    vocal_separations} ID 들."""
    return {
        "id": gen_uuid(),
        "material_id": material_id,
        "extra_material_refs": [
            refs["speeds"], refs["placeholder_infos"], refs["beats"],
            refs["sound_channel_mappings"], refs["vocal_separations"],
        ],
        "source_timerange": {"start": 0, "duration": duration_us},
        "target_timerange": {"start": target_start_us, "duration": duration_us},
        "render_timerange": {"start": 0, "duration": 0},
        "desc": "", "state": 0, "speed": 1.0,
        "is_loop": False, "is_tone_modify": False, "reverse": False,
        "intensifies_audio": False, "cartoon": False,
        "volume": 1.0, "last_nonzero_volume": 1.0,
        "clip": None, "uniform_scale": None,
        "render_index": render_index, "keyframe_refs": [],
        "enable_lut": False, "enable_adjust": False, "enable_hsl": False,
        "visible": True, "group_id": "",
        "enable_color_curves": False, "enable_hsl_curves": False,
        "track_render_index": 0, "hdr_settings": None,
        "enable_color_wheels": False, "track_attribute": 0,
        "is_placeholder": False, "template_id": "",
        "enable_smart_color_adjust": False, "template_scene": "default",
        "common_keyframes": [], "caption_info": None,
        "responsive_layout": {"enable": False, "target_follow": "", "size_layout": 0,
                              "horizontal_pos_layout": 0, "vertical_pos_layout": 0},
        "source": "segmentsourcenormal",
    }


# ─── 메인 빌더 ─────────────────────────────────────────
def build_draft_content(pairs: list[dict], canvas_w: int, canvas_h: int, fps: int,
                        draft_root_for_resources: str) -> tuple[dict, str, int]:
    """pairs 는 [{image_path, image_name, audio_path, audio_name, w, h, duration_us}, ...]
    반환: (draft_content_json, draft_id, total_duration_us)
    """
    draft_id = gen_uuid()

    # 자료 컨테이너
    videos, audios = [], []
    canvases, material_colors, loudnesses = [], [], []
    beats = []
    speeds_list, sound_channel_mappings, vocal_separations, placeholder_infos = [], [], [], []

    # 트랙
    video_track = {"id": gen_uuid(), "type": "video", "segments": [],
                   "flag": 0, "attribute": 0, "name": "", "is_default_name": True}
    audio_track = {"id": gen_uuid(), "type": "audio", "segments": [],
                   "flag": 0, "attribute": 0, "name": "", "is_default_name": True}

    cumulative_us = 0
    total_us = 0

    for idx, p in enumerate(pairs):
        # 이미지 자료
        v_resource_path = f"{draft_root_for_resources}/Resources/{p['image_name']}"
        v_mat = make_video_material(v_resource_path, p["image_name"], p["w"], p["h"])
        videos.append(v_mat)

        # 오디오 자료
        a_resource_path = f"{draft_root_for_resources}/Resources/{p['audio_name']}"
        a_mat = make_audio_material(a_resource_path, p["audio_name"], p["duration_us"])
        audios.append(a_mat)

        # video segment refs (7종)
        v_refs = {
            "speeds": (s := make_speed())["id"],
            "placeholder_infos": (pi := make_placeholder_info())["id"],
            "canvases": (cv := make_canvas())["id"],
            "sound_channel_mappings": (scm := make_sound_channel_mapping())["id"],
            "material_colors": (mc := make_material_color())["id"],
            "loudnesses": (ld := make_loudness())["id"],
            "vocal_separations": (vs := make_vocal_separation())["id"],
        }
        speeds_list.append(s); placeholder_infos.append(pi); canvases.append(cv)
        sound_channel_mappings.append(scm); material_colors.append(mc)
        loudnesses.append(ld); vocal_separations.append(vs)

        # audio segment refs (5종)
        a_refs = {
            "speeds": (a_s := make_speed())["id"],
            "placeholder_infos": (a_pi := make_placeholder_info())["id"],
            "beats": (b := make_beat())["id"],
            "sound_channel_mappings": (a_scm := make_sound_channel_mapping())["id"],
            "vocal_separations": (a_vs := make_vocal_separation())["id"],
        }
        speeds_list.append(a_s); placeholder_infos.append(a_pi); beats.append(b)
        sound_channel_mappings.append(a_scm); vocal_separations.append(a_vs)

        # segments
        v_seg = make_video_segment(v_mat["id"], v_refs, cumulative_us, p["duration_us"], render_index=idx)
        a_seg = make_audio_segment(a_mat["id"], a_refs, cumulative_us, p["duration_us"], render_index=idx)
        video_track["segments"].append(v_seg)
        audio_track["segments"].append(a_seg)

        cumulative_us += p["duration_us"]
        total_us = cumulative_us

    # 트랙에 timeline_id 적용 (timeline_layout.json 과 매칭)
    # CapCut 은 사실 트랙 UUID 와 별개로 timeline 을 관리하지만,
    # 여기서는 video_track 의 id 를 timeline_id 로 사용해도 무방.
    # (timeline_layout 은 CapCut UI 가 갱신하는 메타라 정확한 매칭 안 해도 되는 것으로 관찰)

    content = {
        "canvas_config": {"background": None, "height": canvas_h, "ratio": "16:9", "width": canvas_w},
        "color_space": 0,
        "config": {
            "adjust_max_index": 1, "attachment_info": [], "combination_max_index": 1,
            "export_range": None, "extract_audio_last_index": 1,
            "lyrics_recognition_id": "", "lyrics_sync": True, "lyrics_taskinfo": [],
            "maintrack_adsorb": True, "material_save_mode": 0,
            "multi_language_current": "none", "multi_language_list": [],
            "multi_language_main": "none", "multi_language_mode": "none",
            "original_sound_last_index": 1, "record_audio_last_index": 1,
            "sticker_max_index": 1, "subtitle_keywords_config": None,
            "subtitle_recognition_id": "", "subtitle_sync": True,
            "subtitle_taskinfo": [], "system_font_list": [],
            "use_clear_video_setting": False, "use_quick_brush": False,
            "use_quick_eraser": False, "video_mute": False, "zoom_info_params": None,
        },
        "cover": None, "create_time": 0, "draft_type": "video",
        "duration": total_us, "extra_info": None, "fps": float(fps),
        "free_render_index_mode_on": False,
        "function_assistant_info": {f"{k}_extra_info": {} for k in [
            "ai_audio", "ai_lyric_video", "ai_packaging", "ai_packaging_extra_v2",
            "ai_pic_to_video", "ai_storyboard", "ai_video", "auto_clean", "auto_compose",
            "auto_subtitle", "broll_to_video", "captions_to_video", "color_correct",
            "commerce_template", "compose", "draft", "drama", "expand_video",
            "extract_template", "im_to_im", "image_to_video", "live_photo",
            "long_video_to_short", "magic_brush", "magic_video", "manual_template",
            "math_video", "merge", "object_remove", "old_photo", "pic_to_video",
            "pic_video", "scene_to_video", "skin_smooth", "speed_change",
            "subtitle_align", "text_to_video", "tts", "video_summary", "video_to_text",
        ]},
        "group_container": None, "id": draft_id,
        "is_drop_frame_timecode": False, "keyframe_graph_list": [],
        "keyframes": {"adjusts": [], "audios": [], "effects": [], "filters": [],
                      "handwrites": [], "stickers": [], "texts": [], "videos": []},
        "last_modified_platform": {"app_id": CAPCUT_APP_ID, "app_source": "cc",
                                   "app_version": CAPCUT_APP_VERSION, "device_id": "",
                                   "hard_disk_id": "", "mac_address": "", "os": CAPCUT_OS,
                                   "os_version": CAPCUT_OS_VERSION},
        "lyrics_effects": [],
        "materials": {
            "ai_translates": [], "audio_balances": [], "audio_effects": [],
            "audio_fades": [], "audio_pannings": [], "audio_pitch_shifts": [],
            "audio_track_indexes": [], "audios": audios, "beats": beats,
            "canvases": canvases, "chromas": [], "color_curves": [],
            "common_mask": [], "digital_human_model_dressing": [], "digital_humans": [],
            "drafts": [], "effects": [], "flowers": [], "green_screens": [],
            "handwrites": [], "hsl": [], "hsl_curves": [], "images": [],
            "log_color_wheels": [], "loudnesses": loudnesses, "manual_beautys": [],
            "manual_deformations": [], "material_animations": [],
            "material_colors": material_colors, "multi_language_refs": [],
            "placeholder_infos": placeholder_infos, "placeholders": [],
            "plugin_effects": [], "primary_color_wheels": [], "realtime_denoises": [],
            "shapes": [], "smart_crops": [], "smart_relights": [],
            "sound_channel_mappings": sound_channel_mappings, "speeds": speeds_list,
            "stickers": [], "tail_leaders": [], "text_templates": [], "texts": [],
            "time_marks": [], "transitions": [], "video_effects": [],
            "video_radius": [], "video_shadows": [], "video_strokes": [],
            "video_trackings": [], "videos": videos, "vocal_beautifys": [],
            "vocal_separations": vocal_separations,
        },
        "mutable_config": None, "name": "", "new_version": "167.0.0", "path": "",
        "platform": {"app_id": CAPCUT_APP_ID, "app_source": "cc",
                     "app_version": CAPCUT_APP_VERSION, "device_id": "",
                     "hard_disk_id": "", "mac_address": "", "os": CAPCUT_OS,
                     "os_version": CAPCUT_OS_VERSION},
        "relationships": [], "render_index_track_mode_on": True,
        "retouch_cover": None,
        "smart_ads_info": {"draft_id": "", "mode": 0, "task_id": ""},
        "source": "default", "static_cover_image_path": "", "time_marks": None,
        "tracks": [video_track, audio_track],
        "uneven_animation_template_info": {"layout_path": "", "music_id": "",
                                           "music_path": "", "music_set_by_user": False},
        "update_time": 0, "version": 360000,
    }
    return content, draft_id, total_us


def build_meta_info(draft_id: str, draft_name: str, draft_fold_path: str,
                    draft_root_path: str, pairs: list[dict],
                    total_duration_us: int, materials_size_bytes: int) -> dict:
    """draft_meta_info.json 생성. draft_materials 의 type=0 에 이미지+오디오 등록."""
    create_time_unix = int(time.time())
    create_time_us = now_us()

    type0_value = []
    for p in pairs:
        # 이미지 항목
        type0_value.append({
            "ai_group_type": "", "create_time": create_time_unix,
            "duration": p["duration_us"], "enter_from": 0,
            "extra_info": p["image_name"],
            "file_Path": f"{draft_fold_path}/Resources/{p['image_name']}",
            "height": p["h"], "id": gen_uuid(),
            "import_time": create_time_unix, "import_time_ms": create_time_us,
            "item_source": 1, "md5": "", "metetype": "photo",
            "roughcut_time_range": {"duration": p["duration_us"], "start": 0},
            "sub_time_range": {"duration": -1, "start": -1},
            "type": 0, "width": p["w"],
        })
    for p in pairs:
        # 오디오 항목
        type0_value.append({
            "ai_group_type": "", "create_time": create_time_unix,
            "duration": p["duration_us"], "enter_from": 0,
            "extra_info": p["audio_name"],
            "file_Path": f"{draft_fold_path}/Resources/{p['audio_name']}",
            "height": 0, "id": gen_uuid(),
            "import_time": create_time_unix, "import_time_ms": create_time_us,
            "item_source": 1, "md5": "", "metetype": "music",
            "roughcut_time_range": {"duration": p["duration_us"], "start": 0},
            "sub_time_range": {"duration": -1, "start": -1},
            "type": 0, "width": 0,
        })

    return {
        "cloud_draft_cover": False, "cloud_draft_sync": False,
        "cloud_package_completed_time": "",
        "draft_cloud_capcut_purchase_info": "",
        "draft_cloud_last_action_download": False,
        "draft_cloud_package_type": "", "draft_cloud_purchase_info": "",
        "draft_cloud_template_id": "", "draft_cloud_tutorial_info": "",
        "draft_cloud_videocut_purchase_info": "",
        "draft_cover": "draft_cover.jpg", "draft_deeplink_url": "",
        "draft_enterprise_info": {"draft_enterprise_extra": "",
                                  "draft_enterprise_id": "",
                                  "draft_enterprise_name": "",
                                  "enterprise_material": []},
        "draft_fold_path": draft_fold_path, "draft_id": draft_id,
        "draft_is_ae_produce": False, "draft_is_ai_packaging_used": False,
        "draft_is_ai_shorts": False, "draft_is_ai_translate": False,
        "draft_is_article_video_draft": False,
        "draft_is_cloud_temp_draft": False,
        "draft_is_from_deeplink": "false",
        "draft_is_invisible": False, "draft_is_web_article_video": False,
        "draft_materials": [
            {"type": 0, "value": type0_value},
            {"type": 1, "value": []}, {"type": 2, "value": []},
            {"type": 3, "value": []}, {"type": 6, "value": []},
            {"type": 7, "value": []}, {"type": 8, "value": []},
        ],
        "draft_materials_copied_info": [],
        "draft_name": draft_name,
        "draft_need_rename_folder": False, "draft_new_version": "",
        "draft_removable_storage_device": "",
        "draft_root_path": draft_root_path,
        "draft_segment_extra_info": [],
        "draft_timeline_materials_size_": materials_size_bytes,
        "draft_type": "", "draft_web_article_video_enter_from": "",
        "tm_draft_cloud_completed": "", "tm_draft_cloud_entry_id": -1,
        "tm_draft_cloud_modified": 0, "tm_draft_cloud_parent_entry_id": -1,
        "tm_draft_cloud_space_id": -1, "tm_draft_cloud_user_id": -1,
        "tm_draft_create": create_time_us, "tm_draft_modified": create_time_us,
        "tm_draft_removed": 0, "tm_duration": total_duration_us,
    }


# ─── 자산 스캔 ─────────────────────────────────────────
def scan_workspace(workspace: Path) -> list[dict]:
    """images/ 와 audio/ 를 스캔해서 ch{NN}_{SS} 패턴으로 페어링.

    반환: [{image_path, image_name, audio_path, audio_name, w, h, duration_us}, ...]
    """
    images_dir = workspace / "images"
    audio_dir = workspace / "audio"
    if not images_dir.is_dir() or not audio_dir.is_dir():
        raise FileNotFoundError(f"images/ 또는 audio/ 폴더 없음: {workspace}")

    images = sorted(p for p in images_dir.iterdir()
                    if p.suffix.lower() in (".jpeg", ".jpg", ".png"))
    audios = sorted(p for p in audio_dir.iterdir() if p.suffix.lower() == ".wav")

    if len(images) != len(audios):
        raise ValueError(f"이미지({len(images)}개) ≠ 오디오({len(audios)}개)")
    if not images:
        raise ValueError(f"자산 0개. images/ 와 audio/ 가 비어있음.")

    pairs = []
    for img, aud in zip(images, audios):
        w, h = image_size(img)
        dur_us = wav_duration_us(aud)
        pairs.append({
            "image_path": img, "image_name": img.name,
            "audio_path": aud, "audio_name": aud.name,
            "w": w, "h": h, "duration_us": dur_us,
        })
    return pairs


# ─── 부속 파일 처리 ────────────────────────────────────
def write_ancillary_files(draft_dir: Path, timeline_id: str, tm_create_unix: int) -> None:
    """templates/ 의 부속 파일들을 draft_dir 에 복사하면서 placeholder 치환."""
    if not TEMPLATE_DIR.is_dir():
        raise FileNotFoundError(f"templates 폴더 없음: {TEMPLATE_DIR}")

    static_files = ["attachment_editing.json", "draft_agency_config.json",
                    "draft_biz_config.json", "draft_virtual_store.json",
                    "key_value.json", "performance_opt_info.json"]
    for fn in static_files:
        src = TEMPLATE_DIR / fn
        if src.is_file():
            shutil.copy2(src, draft_dir / fn)

    # 동적 placeholder 치환
    settings_tpl = (TEMPLATE_DIR / "draft_settings").read_text(encoding="utf-8")
    settings = (settings_tpl
                .replace("{{TM_CREATE}}", str(tm_create_unix))
                .replace("{{TM_MODIFIED}}", str(tm_create_unix)))
    (draft_dir / "draft_settings").write_text(settings, encoding="utf-8")

    timeline_tpl = (TEMPLATE_DIR / "timeline_layout.json").read_text(encoding="utf-8")
    timeline = timeline_tpl.replace("{{TIMELINE_ID}}", timeline_id)
    (draft_dir / "timeline_layout.json").write_text(timeline, encoding="utf-8")


def make_empty_subdirs(draft_dir: Path) -> None:
    """CapCut 이 기대하는 빈 하위 폴더들 생성."""
    for sub in ("adjust_mask", "common_attachment", "matting",
                "qr_upload", "Resources", "smart_crop", "subdraft"):
        (draft_dir / sub).mkdir(exist_ok=True)


# ─── 엔트리포인트 ──────────────────────────────────────
def build(workspace: Path, output_dir: Path, draft_name: str,
          canvas_w: int, canvas_h: int, fps: int) -> tuple[Path, dict]:
    """전체 빌드 파이프라인. (draft_dir, summary_dict) 반환."""
    pairs = scan_workspace(workspace)
    print(f"[info] 자산 페어 {len(pairs)}개 스캔: {workspace}")

    # 출력 폴더 준비
    if output_dir.exists():
        print(f"[warn] 기존 폴더 삭제: {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    # 빈 하위 폴더 생성 + Resources/ 에 자산 복사
    make_empty_subdirs(output_dir)
    res_dir = output_dir / "Resources"
    materials_size = 0
    for p in pairs:
        dst_img = res_dir / p["image_name"]
        dst_aud = res_dir / p["audio_name"]
        shutil.copy2(p["image_path"], dst_img)
        shutil.copy2(p["audio_path"], dst_aud)
        materials_size += dst_img.stat().st_size + dst_aud.stat().st_size
    print(f"[info] Resources/ 복사 완료, 합계 {materials_size:,} bytes")

    # draft_content.json
    draft_fold_path = str(output_dir).replace("\\", "/")
    content, draft_id, total_us = build_draft_content(
        pairs, canvas_w, canvas_h, fps, draft_fold_path)
    timeline_id = content["tracks"][0]["id"]  # video track id 를 timeline 으로
    (output_dir / "draft_content.json").write_text(
        json.dumps(content, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8")
    print(f"[info] draft_content.json 생성, draft_id={draft_id}, 길이 {total_us//1_000_000}.{(total_us//1000)%1000:03d}초")

    # draft_meta_info.json
    draft_root_path = str(output_dir.parent).replace("\\", "/")  # 임시 (install 시 갱신됨)
    meta = build_meta_info(draft_id, draft_name, draft_fold_path, draft_root_path,
                           pairs, total_us, materials_size)
    (output_dir / "draft_meta_info.json").write_text(
        json.dumps(meta, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8")
    print(f"[info] draft_meta_info.json 생성")

    # 부속 파일들
    write_ancillary_files(output_dir, timeline_id, int(time.time()))

    # draft_cover.jpg — 첫 이미지 사용
    if pairs and pairs[0]["image_path"].suffix.lower() in (".jpg", ".jpeg"):
        shutil.copy2(pairs[0]["image_path"], output_dir / "draft_cover.jpg")
    else:
        # fallback: 1x1 검정 jpeg
        (output_dir / "draft_cover.jpg").write_bytes(
            bytes.fromhex("ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432ffc0000b08000100010101011100ffc4001f0000010501010101010100000000000000000102030405060708090a0bffc4001f00010001050101010101010000000000000000010203040506070809ffda0008010100003f00fb0000ffd9"))

    summary = {
        "draft_id": draft_id, "draft_name": draft_name,
        "draft_dir": str(output_dir), "scenes": len(pairs),
        "total_duration_us": total_us, "materials_size_bytes": materials_size,
        "timeline_id": timeline_id,
    }
    return output_dir, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="CapCut 8.x 드래프트 자동 빌더")
    parser.add_argument("chapter", help="챕터 번호 (예: 02)")
    parser.add_argument("--workspace", default=None,
                        help="workspace 루트 (default: ./workspace)")
    parser.add_argument("--output", default=None,
                        help="출력 폴더 (default: workspace/ch{NN}/draft)")
    parser.add_argument("--name", default=None,
                        help="드래프트 이름 (default: ch{NN}_draft_{YYYYMMDD})")
    parser.add_argument("--canvas-w", type=int, default=DEFAULT_CANVAS_W)
    parser.add_argument("--canvas-h", type=int, default=DEFAULT_CANVAS_H)
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS)
    args = parser.parse_args()

    chapter = args.chapter.zfill(2)
    ws_root = Path(args.workspace) if args.workspace else Path.cwd() / "workspace"
    workspace = ws_root / f"ch{chapter}"
    if not workspace.is_dir():
        print(f"[error] workspace 없음: {workspace}", file=sys.stderr)
        return 2

    output_dir = Path(args.output) if args.output else workspace / "draft"
    draft_name = args.name or f"ch{chapter}_draft_{time.strftime('%Y%m%d')}"

    try:
        draft_dir, summary = build(workspace, output_dir, draft_name,
                                   args.canvas_w, args.canvas_h, args.fps)
    except (FileNotFoundError, ValueError) as e:
        print(f"[error] {e}", file=sys.stderr)
        return 1

    print(f"\n[ok] 빌드 완료: {draft_dir}")
    print(f"     draft_id: {summary['draft_id']}")
    print(f"     씬 {summary['scenes']}개, 길이 {summary['total_duration_us']//1_000_000}초, "
          f"자료 {summary['materials_size_bytes']:,} bytes")
    print(f"\n다음 단계:")
    print(f"  python install_draft.py {chapter}        # CapCut 에 설치")
    return 0


if __name__ == "__main__":
    sys.exit(main())
