"""
Target hysteresis + EMA smoothing helper for aiming stability.
"""
import math


class TargetSmoother:
    def __init__(self, ema_alpha=0.35, switch_confirm_frames=3, switch_radius_px=18.0):
        self.ema_alpha = float(ema_alpha)
        self.switch_confirm_frames = max(1, int(switch_confirm_frames))
        self.switch_radius_px = float(switch_radius_px)
        self.last_target = None
        self.stable_candidate = None
        self.stable_count = 0

    @staticmethod
    def _unpack_target(target):
        if len(target) >= 5:
            cx, cy, _, head_y_min, body_y_max = target[:5]
        else:
            cx, cy, _ = target[:3]
            head_y_min, body_y_max = None, None
        return float(cx), float(cy), head_y_min, body_y_max

    @staticmethod
    def _same_candidate(a, b, radius):
        if a is None or b is None:
            return False
        return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1])) <= float(radius)

    def stabilize(self, targets, center_x, center_y):
        if not targets:
            self.stable_candidate = None
            self.stable_count = 0
            return []

        best_target = min(targets, key=lambda t: t[2])
        cand_x, cand_y, cand_head_y_min, cand_body_y_max = self._unpack_target(best_target)

        if self.last_target is None:
            self.last_target = (cand_x, cand_y, cand_head_y_min, cand_body_y_max)
            distance = math.hypot(cand_x - center_x, cand_y - center_y)
            return [(cand_x, cand_y, distance, cand_head_y_min, cand_body_y_max)]

        last_x, last_y, last_head_y_min, last_body_y_max = self.last_target
        switch_radius = max(6.0, self.switch_radius_px)
        candidate_far = math.hypot(cand_x - last_x, cand_y - last_y) > switch_radius

        desired_x = cand_x
        desired_y = cand_y
        desired_head_y_min = cand_head_y_min
        desired_body_y_max = cand_body_y_max

        if candidate_far:
            if self._same_candidate(self.stable_candidate, (cand_x, cand_y), switch_radius):
                self.stable_count += 1
            else:
                self.stable_candidate = (cand_x, cand_y)
                self.stable_count = 1

            if self.stable_count < self.switch_confirm_frames:
                desired_x = last_x
                desired_y = last_y
                desired_head_y_min = last_head_y_min
                desired_body_y_max = last_body_y_max
            else:
                self.stable_candidate = None
                self.stable_count = 0
        else:
            self.stable_candidate = None
            self.stable_count = 0

        alpha = max(0.0, min(1.0, self.ema_alpha))
        smooth_x = last_x + alpha * (desired_x - last_x)
        smooth_y = last_y + alpha * (desired_y - last_y)

        self.last_target = (smooth_x, smooth_y, desired_head_y_min, desired_body_y_max)
        distance = math.hypot(smooth_x - center_x, smooth_y - center_y)
        return [(smooth_x, smooth_y, distance, desired_head_y_min, desired_body_y_max)]
