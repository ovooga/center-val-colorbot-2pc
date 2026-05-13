from src.utils.debug_logger import log_print
import cv2
import numpy as np

from src.utils.config import config


_model = None
_class_names = {}
HSV_MIN = None
HSV_MAX = None


def test():
    log_print("HSV Detection test initialized")
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    _ = cv2.cvtColor(dummy_img, cv2.COLOR_BGR2HSV)
    log_print("HSV conversion done")


def load_model(model_path=None):
    global _model, _class_names, HSV_MIN, HSV_MAX
    config.model_load_error = ""

    try:
        log_print("Loading HSV parameters...")
        yellow = [18, 80, 80, 40, 255, 255]
        purple = [125, 60, 80, 170, 255, 255]
        red = [0, 95, 95, 4, 235, 255]

        if config.color == "yellow":
            HSV_MIN = np.array([yellow[0], yellow[1], yellow[2]], dtype=np.uint8)
            HSV_MAX = np.array([yellow[3], yellow[4], yellow[5]], dtype=np.uint8)
            log_print("Loaded HSV for yellow")
        elif config.color == "purple":
            HSV_MIN = np.array([purple[0], purple[1], purple[2]], dtype=np.uint8)
            HSV_MAX = np.array([purple[3], purple[4], purple[5]], dtype=np.uint8)
            log_print("Loaded HSV for purple")
        elif config.color == "red":
            HSV_MIN = np.array([red[0], red[1], red[2]], dtype=np.uint8)
            HSV_MAX = np.array([red[3], red[4], red[5]], dtype=np.uint8)
            log_print("Loaded HSV for red")
        elif config.color == "custom":
            HSV_MIN = np.array(
                [
                    getattr(config, "custom_hsv_min_h", 0),
                    getattr(config, "custom_hsv_min_s", 0),
                    getattr(config, "custom_hsv_min_v", 0),
                ],
                dtype=np.uint8,
            )
            HSV_MAX = np.array(
                [
                    getattr(config, "custom_hsv_max_h", 179),
                    getattr(config, "custom_hsv_max_s", 255),
                    getattr(config, "custom_hsv_max_v", 255),
                ],
                dtype=np.uint8,
            )
            log_print(f"Loaded custom HSV: MIN={HSV_MIN}, MAX={HSV_MAX}")
        else:
            raise ValueError(f"Unknown color {config.color}")

        _model = (HSV_MIN, HSV_MAX)
        _class_names = {"color": "Target Color"}
        config.model_classes = list(_class_names.values())
        config.model_file_size = 0
        return _model, _class_names
    except Exception as exc:
        config.model_load_error = f"Failed to load HSV params: {exc}"
        _model, _class_names = None, {}
        return None, {}


def reload_model(model_path=None):
    return load_model(model_path)


def has_color_vertical_line(mask, x, y1, y2):
    x = int(max(0, min(x, mask.shape[1] - 1)))
    y1 = int(max(0, min(y1, mask.shape[0])))
    y2 = int(max(0, min(y2, mask.shape[0])))
    if y2 <= y1:
        return False
    line = mask[y1:y2, x]
    return bool(np.any(line > 0))


def _bbox_area(rect):
    _, _, w, h = rect
    return max(0, int(w)) * max(0, int(h))


def _touches_border(rect, img_w, img_h, margin=1):
    x, y, w, h = rect
    return (
        x <= margin
        or y <= margin
        or (x + w) >= (img_w - margin)
        or (y + h) >= (img_h - margin)
    )


def _boxes_overlap(r1, r2):
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    return (x1 < x2 + w2 and x1 + w1 > x2) and (y1 < y2 + h2 and y1 + h1 > y2)


def _overlap_len(a0, a1, b0, b1):
    return max(0, min(a1, b1) - max(a0, b0))


def _boxes_should_merge(r1, r2, dist_threshold):
    if _boxes_overlap(r1, r2):
        return True

    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    x1r, y1r = x1 + w1, y1 + h1
    x2r, y2r = x2 + w2, y2 + h2

    h_gap = max(0, max(x1, x2) - min(x1r, x2r))
    v_gap = max(0, max(y1, y2) - min(y1r, y2r))
    h_overlap = _overlap_len(x1, x1r, x2, x2r)
    v_overlap = _overlap_len(y1, y1r, y2, y2r)

    a1 = max(1, _bbox_area(r1))
    a2 = max(1, _bbox_area(r2))
    area_ratio = min(a1, a2) / max(a1, a2)
    # Merge mainly fragment-like splits; avoid merging similarly sized players.
    is_fragment = area_ratio <= 0.80
    if not is_fragment:
        return False

    close_h = h_gap <= dist_threshold and v_overlap >= 0.60 * min(h1, h2)
    close_v = v_gap <= dist_threshold and h_overlap >= 0.60 * min(w1, w2)
    return close_h or close_v


def merge_close_rects(rects, centers, dist_threshold=None):
    if dist_threshold is None:
        dist_threshold = int(getattr(config, "detection_merge_distance", 12))
    dist_threshold = int(max(0, min(dist_threshold, 18)))

    output_rects = []
    output_centers = []
    used = [False] * len(rects)

    for i, (r1, c1) in enumerate(zip(rects, centers)):
        if used[i]:
            continue

        x1, y1, w1, h1 = r1
        nx1, ny1 = x1, y1
        nx2, ny2 = x1 + w1, y1 + h1

        changed = True
        while changed:
            changed = False
            current_rect = (nx1, ny1, nx2 - nx1, ny2 - ny1)
            for j, r2 in enumerate(rects):
                if i == j or used[j]:
                    continue
                if _boxes_should_merge(current_rect, r2, dist_threshold):
                    x2, y2, w2, h2 = r2
                    nx1 = min(nx1, x2)
                    ny1 = min(ny1, y2)
                    nx2 = max(nx2, x2 + w2)
                    ny2 = max(ny2, y2 + h2)
                    used[j] = True
                    changed = True

        used[i] = True
        final_w = max(1, nx2 - nx1)
        final_h = max(1, ny2 - ny1)
        final_cx = int(nx1 + final_w // 2)
        final_cy = int(ny1 + final_h // 2)
        output_rects.append((nx1, ny1, final_w, final_h))
        output_centers.append((final_cx, final_cy))

    sort_idx = sorted(range(len(output_rects)), key=lambda idx: _bbox_area(output_rects[idx]), reverse=True)
    output_rects = [output_rects[idx] for idx in sort_idx]
    output_centers = [output_centers[idx] for idx in sort_idx]

    return output_rects, output_centers


def _is_split_mode_enabled():
    split_mode = str(getattr(config, "detection_split_mode", "watershed")).strip().lower()
    return split_mode in {"watershed", "ws", "instance"}


def _should_try_watershed_split(rect, contour_area, frame_area):
    x, y, w, h = rect
    if int(w) < 2 or int(h) < 2:
        return False

    trigger_area_default = max(120, int(frame_area * 0.0012))
    trigger_area = int(getattr(config, "detection_split_trigger_area", trigger_area_default))
    trigger_area = max(40, min(trigger_area, max(80, int(frame_area * 0.10))))

    trigger_aspect = float(getattr(config, "detection_split_trigger_aspect", 1.15))
    trigger_aspect = max(0.8, min(trigger_aspect, 6.0))

    bbox_area = int(w) * int(h)
    aspect = float(w) / max(float(h), 1.0)
    min_contour_for_split = max(24.0, float(trigger_area) * 0.22)
    return bbox_area >= trigger_area and aspect >= trigger_aspect and contour_area >= min_contour_for_split


def _split_blob_watershed(image, mask, rect, min_instance_area, dist_ratio):
    x, y, w, h = rect
    pad = int(getattr(config, "detection_split_padding", 1))
    pad = max(0, min(pad, 4))

    x0 = max(0, int(x) - pad)
    y0 = max(0, int(y) - pad)
    x1 = min(mask.shape[1], int(x) + int(w) + pad)
    y1 = min(mask.shape[0], int(y) + int(h) + pad)
    if x1 <= x0 or y1 <= y0:
        return []

    roi_mask = mask[y0:y1, x0:x1]
    roi_img = image[y0:y1, x0:x1]
    if roi_mask.size == 0 or roi_img.size == 0:
        return []

    binary = np.where(roi_mask > 0, 255, 0).astype(np.uint8)
    if cv2.countNonZero(binary) < max(min_instance_area * 2, 32):
        return []

    dist_map = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
    max_dist = float(dist_map.max())
    if max_dist <= 0.0:
        return []

    dist_ratio = max(0.20, min(float(dist_ratio), 0.85))
    _, sure_fg = cv2.threshold(dist_map, dist_ratio * max_dist, 255, cv2.THRESH_BINARY)
    sure_fg = sure_fg.astype(np.uint8)
    sure_fg = cv2.morphologyEx(sure_fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

    marker_count, markers = cv2.connectedComponents(sure_fg)
    if marker_count <= 2:
        return []

    unknown = cv2.subtract(binary, sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    ws_input = roi_img if roi_img.ndim == 3 else cv2.cvtColor(roi_img, cv2.COLOR_GRAY2BGR)
    ws_markers = cv2.watershed(ws_input.copy(), markers)

    found_rects = []
    for marker_id in np.unique(ws_markers):
        if marker_id <= 1:
            continue
        component = np.uint8(ws_markers == marker_id) * 255
        component_area = int(cv2.countNonZero(component))
        if component_area < int(min_instance_area):
            continue
        component_contours, _ = cv2.findContours(component, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not component_contours:
            continue
        largest = max(component_contours, key=cv2.contourArea)
        sx, sy, sw, sh = cv2.boundingRect(largest)
        if int(sw) <= 0 or int(sh) <= 0:
            continue
        found_rects.append((x0 + int(sx), y0 + int(sy), int(sw), int(sh), float(component_area)))

    if len(found_rects) < 2:
        return []

    found_rects.sort(key=lambda r: r[4], reverse=True)
    filtered_rects = []
    for rect_candidate in found_rects:
        cx, cy, cw, ch, _ = rect_candidate
        keep = True
        for existing in filtered_rects:
            ex, ey, ew, eh, _ = existing
            inter_w = max(0, min(cx + cw, ex + ew) - max(cx, ex))
            inter_h = max(0, min(cy + ch, ey + eh) - max(cy, ey))
            inter = inter_w * inter_h
            union = (cw * ch) + (ew * eh) - inter
            if union > 0 and (inter / union) > 0.65:
                keep = False
                break
        if keep:
            filtered_rects.append(rect_candidate)

    return filtered_rects


def _split_blob_projection(mask, rect, min_instance_area):
    x, y, w, h = rect
    if int(w) < 4 or int(h) < 4:
        return []

    roi_mask = mask[int(y) : int(y) + int(h), int(x) : int(x) + int(w)]
    if roi_mask.size == 0:
        return []

    binary = np.where(roi_mask > 0, 1, 0).astype(np.uint8)
    if int(binary.sum()) < max(int(min_instance_area) * 2, 20):
        return []

    column_sum = binary.sum(axis=0).astype(np.float32)
    smooth_window = int(getattr(config, "detection_projection_smooth_window", 5))
    smooth_window = max(1, min(smooth_window, 13))
    if smooth_window % 2 == 0:
        smooth_window += 1
    if smooth_window > 1:
        kernel = np.ones((smooth_window,), dtype=np.float32) / float(smooth_window)
        column_sum = np.convolve(column_sum, kernel, mode="same")

    gap_ratio = float(getattr(config, "detection_projection_gap_ratio", 0.08))
    gap_ratio = max(0.02, min(gap_ratio, 0.40))
    gap_threshold = max(1.0, float(h) * gap_ratio)

    active = column_sum > gap_threshold
    col_segments = []
    start = None
    for idx, is_active in enumerate(active):
        if is_active and start is None:
            start = idx
        elif (not is_active) and start is not None:
            col_segments.append((start, idx))
            start = None
    if start is not None:
        col_segments.append((start, int(w)))

    if len(col_segments) < 2:
        return []

    min_segment_width = int(getattr(config, "detection_projection_min_segment_width", 3))
    min_segment_width = max(1, min(min_segment_width, max(2, int(w // 2))))

    sub_rects = []
    for sx0, sx1 in col_segments:
        seg_w = int(sx1) - int(sx0)
        if seg_w < min_segment_width:
            continue
        seg = binary[:, int(sx0) : int(sx1)]
        ys, xs = np.where(seg > 0)
        if ys.size == 0:
            continue
        seg_area = int(ys.size)
        if seg_area < int(min_instance_area):
            continue
        sy0 = int(ys.min())
        sy1 = int(ys.max()) + 1
        sw = max(1, seg_w)
        sh = max(1, sy1 - sy0)
        sub_rects.append((int(x) + int(sx0), int(y) + sy0, sw, sh, float(seg_area)))

    return sub_rects if len(sub_rects) >= 2 else []


def triggerbot_detect(model, roi):
    if model is None or roi is None:
        return False
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi, model[0], model[1])
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return bool(np.any(mask > 0))


def perform_detection(model, image):
    if model is None or image is None:
        return [], None

    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    raw_mask = cv2.inRange(hsv_img, model[0], model[1])
    mask = raw_mask.copy()

    # Reference-like morphology path (close + dilate) is the default because it
    # keeps thin color edges that OPEN often removes completely.
    morph_mode = str(getattr(config, "detection_morph_mode", "legacy")).strip().lower()
    if morph_mode == "stable":
        open_kernel_size = int(getattr(config, "detection_open_kernel", 3))
        close_kernel_size = int(getattr(config, "detection_close_kernel", 5))
        blur_kernel_size = int(getattr(config, "detection_mask_blur", 3))
        open_kernel_size = max(1, min(open_kernel_size, 9))
        close_kernel_size = max(1, min(close_kernel_size, 13))
        blur_kernel_size = max(1, min(blur_kernel_size, 7))
        if open_kernel_size % 2 == 0:
            open_kernel_size += 1
        if close_kernel_size % 2 == 0:
            close_kernel_size += 1
        if blur_kernel_size % 2 == 0:
            blur_kernel_size += 1
        open_kernel = np.ones((open_kernel_size, open_kernel_size), np.uint8)
        close_kernel = np.ones((close_kernel_size, close_kernel_size), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, open_kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_kernel)
        if blur_kernel_size >= 3:
            mask = cv2.medianBlur(mask, blur_kernel_size)
    else:
        legacy_kernel_w = int(getattr(config, "detection_legacy_kernel_w", 15))
        legacy_kernel_h = int(getattr(config, "detection_legacy_kernel_h", 9))
        legacy_dilate_iterations = int(getattr(config, "detection_legacy_dilate_iterations", 1))
        legacy_kernel_w = max(1, min(legacy_kernel_w, 40))
        legacy_kernel_h = max(1, min(legacy_kernel_h, 30))
        legacy_dilate_iterations = max(0, min(legacy_dilate_iterations, 3))
        legacy_kernel = np.ones((legacy_kernel_h, legacy_kernel_w), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, legacy_kernel)
        if legacy_dilate_iterations > 0:
            mask = cv2.dilate(mask, legacy_kernel, iterations=legacy_dilate_iterations)

    # If morphology erased all pixels, fall back to raw mask instead of returning empty.
    if cv2.countNonZero(mask) == 0 and cv2.countNonZero(raw_mask) > 0:
        mask = raw_mask

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects, centers = [], []

    img_h, img_w = image.shape[:2]
    frame_area = max(1, img_h * img_w)
    min_bbox_area = int(getattr(config, "detection_min_bbox_area", max(36, int(frame_area * 0.00025))))
    min_contour_area = float(
        getattr(config, "detection_min_contour_area", max(8, int(frame_area * 0.00008)))
    )
    min_fill_ratio = float(getattr(config, "detection_min_fill_ratio", 0.03))
    edge_reject_area = int(
        getattr(config, "detection_edge_reject_area", max(80, int(frame_area * 0.0006)))
    )
    edge_min_contour_area = float(
        getattr(config, "detection_edge_min_contour_area", max(30, int(frame_area * 0.0002)))
    )
    edge_min_side = int(getattr(config, "detection_edge_min_side", 4))
    border_margin = int(getattr(config, "detection_border_margin", 0))
    min_w = int(getattr(config, "detection_min_width", 3))
    min_h = int(getattr(config, "detection_min_height", 4))
    min_aspect = float(getattr(config, "detection_min_aspect", 0.04))
    max_aspect = float(getattr(config, "detection_max_aspect", 6.0))
    require_vertical_line = bool(getattr(config, "detection_require_vertical_line", False))
    min_contour_points = int(getattr(config, "detection_min_contour_points", 5))
    split_enabled = _is_split_mode_enabled()
    split_min_instance_area_default = max(24, int(frame_area * 0.00022))
    split_min_instance_area = int(
        getattr(config, "detection_split_min_instance_area", split_min_instance_area_default)
    )
    split_min_instance_area = max(16, min(split_min_instance_area, max(32, int(frame_area * 0.01))))
    split_dist_ratio = float(getattr(config, "detection_watershed_dist_ratio", 0.42))
    split_dist_ratio = max(0.20, min(split_dist_ratio, 0.85))

    if morph_mode != "stable":
        # Prevent stale strict settings from killing detection in legacy mode.
        min_bbox_area = min(min_bbox_area, max(48, int(frame_area * 0.00045)))
        min_contour_area = min(min_contour_area, max(10, int(frame_area * 0.00010)))
        min_fill_ratio = min(min_fill_ratio, 0.08)

    candidate_list = []
    did_split = False
    for c in contours:
        if len(c) < min_contour_points:
            # Keep simple but large contours (often rectangles) for split/fill checks.
            tx, ty, tw, th = cv2.boundingRect(c)
            if int(tw) * int(th) < max(64, int(split_min_instance_area) * 2):
                continue

        x, y, w, h = cv2.boundingRect(c)
        contour_area = float(cv2.contourArea(c))
        if split_enabled and _should_try_watershed_split((x, y, w, h), contour_area, frame_area):
            split_rects = _split_blob_watershed(
                image, raw_mask, (x, y, w, h), split_min_instance_area, split_dist_ratio
            )
            if len(split_rects) < 2:
                split_rects = _split_blob_projection(raw_mask, (x, y, w, h), split_min_instance_area)
            if len(split_rects) >= 2:
                did_split = True
                candidate_list.extend(split_rects)
                continue
        candidate_list.append((int(x), int(y), int(w), int(h), float(contour_area)))

    for x, y, w, h, contour_area in candidate_list:
        bbox_area = int(w) * int(h)
        if contour_area < min_contour_area:
            continue
        if bbox_area < min_bbox_area:
            continue
        if int(w) < min_w or int(h) < min_h:
            continue

        fill_ratio = contour_area / max(float(bbox_area), 1.0)
        if fill_ratio < min_fill_ratio:
            continue

        aspect = float(w) / max(float(h), 1.0)
        if aspect < min_aspect or aspect > max_aspect:
            continue

        touches_border = _touches_border((x, y, w, h), img_w, img_h, margin=border_margin)
        if touches_border:
            if bbox_area < edge_reject_area:
                continue
            if contour_area < edge_min_contour_area:
                continue
            if min(int(w), int(h)) < edge_min_side:
                continue

        cx, cy = x + w // 2, y + h // 2
        if require_vertical_line and not has_color_vertical_line(mask, cx, y, y + h):
            continue

        rects.append((x, y, w, h))
        centers.append((cx, cy))

    # Fallback pass on raw mask with minimal checks if filtered pass found nothing.
    if not rects and cv2.countNonZero(raw_mask) > 0:
        raw_contours, _ = cv2.findContours(raw_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        loose_min_area = max(20, int(min_bbox_area * 0.5))
        for c in raw_contours:
            x, y, w, h = cv2.boundingRect(c)
            if int(w) * int(h) < loose_min_area:
                continue
            cx, cy = x + w // 2, y + h // 2
            rects.append((x, y, w, h))
            centers.append((cx, cy))

    if not rects:
        return [], mask

    rects_centers = sorted(zip(rects, centers), key=lambda rc: _bbox_area(rc[0]), reverse=True)
    rects = [rc[0] for rc in rects_centers]
    centers = [rc[1] for rc in rects_centers]

    merge_after_split = bool(getattr(config, "detection_merge_after_split", False))
    if did_split and not merge_after_split:
        final_rects = rects
    else:
        final_rects, _ = merge_close_rects(rects, centers)

    return [{"class": "player", "bbox": r, "confidence": 1.0} for r in final_rects], mask


def get_class_names():
    return _class_names


def get_model_size(model_path=None):
    return 0
