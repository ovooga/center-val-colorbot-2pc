import math
from typing import Optional, Tuple


class NCAFController:
    """Nonlinear Close-Aim with Focus (NCAF) controller.

    Implements a 3-zone speed curve (from outside to inside):

        ┌─────────────────────────────┐
        │  Snap Radius (outer, dashed)│   Zone 1: factor = 1.0
        │  ┌───────────────────────┐  │
        │  │ Near Radius (inner)   │  │   Zone 2: smooth transition
        │  │  ┌──── ＋ ────┐       │  │
        │  │  │ Target Ctr │       │  │   Zone 3: α exponent + snap_boost
        │  │  └────────────┘       │  │
        │  └───────────────────────┘  │
        └─────────────────────────────┘

      - Snap Radius (outer): overall engagement zone
      - Near Radius (inner): precision zone, speed tapered by exponent α
      - Snap Boost Factor: base multiplier inside the near zone
      - α (Speed Curve Exponent): controls how aggressively speed drops near center
      - Max Step: limits per-frame movement magnitude

    Note: snap_radius should be >= near_radius. If not, they are auto-swapped.
    """

    def __init__(self) -> None:
        """Initialize NCAF controller (tracking removed - not compatible with color detection)."""
        pass

    @staticmethod
    def compute_ncaf_factor(distance: float,
                            snap_radius: float,
                            near_radius: float,
                            alpha: float,
                            snap_boost: float) -> float:
        """Compute the NCAF speed factor for a given distance.

        Three zones (from outside to inside):
          Zone 1 – outside snap_radius:  factor = 1.0  (full speed)
          Zone 2 – between snap & near:  linear transition 1.0 → snap_boost
          Zone 3 – inside near_radius:   factor = snap_boost × (d / near_radius)^α

        The factor is continuous at every boundary.

        Args:
            distance:    pixel distance from crosshair to target
            snap_radius: outer engagement radius (px)
            near_radius: inner precision radius (px)
            alpha:       speed-curve exponent (>0)
            snap_boost:  base speed multiplier inside the near zone

        Returns:
            speed factor in [0, 1+]
        """
        # Auto-swap so snap (outer) >= near (inner)
        if snap_radius < near_radius:
            snap_radius, near_radius = near_radius, snap_radius

        if distance > snap_radius:
            # Zone 1: outside snap radius — full speed
            return 1.0

        if distance > near_radius:
            # Zone 2: between snap and near — smooth linear transition
            gap = snap_radius - near_radius
            if gap < 1e-6:
                return snap_boost
            t = (snap_radius - distance) / gap   # 0 at snap edge, 1 at near edge
            return 1.0 + t * (snap_boost - 1.0)

        # Zone 3: inside near radius — α exponent precision curve
        if near_radius > 1e-6:
            return snap_boost * (distance / near_radius) ** max(0.0, alpha)
        return snap_boost

    def compute_ncaf_delta(self,
                            dx: float,
                            dy: float,
                            near_radius: float,
                            snap_radius: float,
                            alpha: float,
                            snap_boost: float,
                            max_step: float,
                            min_speed_multiplier: float = 0.01,
                            max_speed_multiplier: float = 10.0) -> Tuple[float, float]:
        """Apply NCAF speed curve to raw delta (dx, dy).

        Uses math.hypot(dx, dy) as the distance metric.
        
        Args:
            dx: X direction delta
            dy: Y direction delta
            near_radius: inner precision radius (px)
            snap_radius: outer engagement radius (px)
            alpha: speed-curve exponent (>0)
            snap_boost: base speed multiplier inside the near zone
            max_step: maximum per-frame movement magnitude (px)
            min_speed_multiplier: minimum speed multiplier (clamps factor)
            max_speed_multiplier: maximum speed multiplier (clamps factor)
        
        Returns:
            tuple: (new_dx, new_dy) adjusted deltas
        """
        distance = math.hypot(dx, dy)
        if distance <= 1e-6:
            return 0.0, 0.0

        factor = self.compute_ncaf_factor(distance, snap_radius, near_radius,
                                          alpha, snap_boost)
        
        # Apply min/max speed multiplier limits
        factor = max(min_speed_multiplier, min(factor, max_speed_multiplier))

        new_dx = dx * factor
        new_dy = dy * factor

        # Limit per-step movement
        step = math.hypot(new_dx, new_dy)
        if max_step > 0 and step > max_step:
            scale = max_step / step
            new_dx *= scale
            new_dy *= scale
        return new_dx, new_dy


_ncaf_singleton: Optional[NCAFController] = None


def get_ncaf_controller() -> NCAFController:
    """Factory returning a shared NCAFController instance."""
    global _ncaf_singleton
    if _ncaf_singleton is None:
        _ncaf_singleton = NCAFController()
    return _ncaf_singleton
