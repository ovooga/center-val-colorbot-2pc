"""
Bezier curve movement module for aimbot mode.

This module provides bezier curve calculation and movement functionality
for smooth, natural mouse movement patterns.
"""

from typing import List, Tuple, Optional


def calculate_bezier_point(
    t: float,
    p0: Tuple[float, float],
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    p3: Tuple[float, float]
) -> Tuple[float, float]:
    """
    Calculate a point on a cubic Bezier curve.
    
    Args:
        t: Parameter value between 0 and 1
        p0: Start point (x, y)
        p1: First control point (x, y)
        p2: Second control point (x, y)
        p3: End point (x, y)
        
    Returns:
        Tuple of (x, y) coordinates on the curve
    """
    u = 1 - t
    tt = t * t
    uu = u * u
    uuu = uu * u
    ttt = tt * t
    
    x = uuu * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0]
    y = uuu * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1]
    
    return (x, y)


def generate_bezier_points(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    ctrl_x: float,
    ctrl_y: float,
    segments: int
) -> List[Tuple[float, float]]:
    """
    Generate points along a Bezier curve from start to end.
    
    Args:
        start_x: Starting X coordinate
        start_y: Starting Y coordinate
        end_x: Ending X coordinate
        end_y: Ending Y coordinate
        ctrl_x: Control point X offset (relative to start)
        ctrl_y: Control point Y offset (relative to start)
        segments: Number of segments to divide the curve into
        
    Returns:
        List of (x, y) tuples representing points along the curve
    """
    if segments <= 0:
        return [(end_x, end_y)]
    
    p0 = (start_x, start_y)
    p1 = (start_x + ctrl_x, start_y + ctrl_y)
    p2 = (end_x - ctrl_x, end_y - ctrl_y)
    p3 = (end_x, end_y)
    
    points = []
    for i in range(segments + 1):
        t = i / segments if segments > 0 else 0
        point = calculate_bezier_point(t, p0, p1, p2, p3)
        points.append(point)
    
    return points


def calculate_bezier_movement_deltas(
    dx: float,
    dy: float,
    ctrl_x: float,
    ctrl_y: float,
    segments: int
) -> List[Tuple[float, float]]:
    """
    Calculate movement deltas for a Bezier curve movement.
    
    This function calculates the incremental movements needed to follow
    a Bezier curve from the origin (0, 0) to the target (dx, dy).
    
    Args:
        dx: Target X movement
        dy: Target Y movement
        ctrl_x: Control point X offset
        ctrl_y: Control point Y offset
        segments: Number of segments to divide the curve into
        
    Returns:
        List of (delta_x, delta_y) tuples for each movement step
    """
    if segments <= 0:
        return [(dx, dy)]
    
    points = generate_bezier_points(0, 0, dx, dy, ctrl_x, ctrl_y, segments)
    
    deltas = []
    prev_x, prev_y = points[0]
    for x, y in points[1:]:
        delta_x = x - prev_x
        delta_y = y - prev_y
        deltas.append((delta_x, delta_y))
        prev_x, prev_y = x, y
    
    return deltas


class BezierMovement:
    """
    Bezier curve movement handler for aimbot mode.
    
    This class provides a clean interface for generating and executing
    Bezier curve movements for mouse control.
    """
    
    def __init__(
        self,
        segments: int = 8,
        ctrl_x: float = 16.0,
        ctrl_y: float = 16.0
    ):
        """
        Initialize Bezier movement handler.
        
        Args:
            segments: Number of segments for the Bezier curve
            ctrl_x: Control point X offset
            ctrl_y: Control point Y offset
        """
        self.segments = max(0, int(segments))
        self.ctrl_x = float(ctrl_x)
        self.ctrl_y = float(ctrl_y)
    
    def generate_movement_command(
        self,
        dx: float,
        dy: float,
        segments: Optional[int] = None,
        ctrl_x: Optional[float] = None,
        ctrl_y: Optional[float] = None
    ) -> str:
        """
        Generate a movement command string for the MAKCU device.
        
        Args:
            dx: Target X movement
            dy: Target Y movement
            segments: Number of segments (uses instance default if None)
            ctrl_x: Control point X offset (uses instance default if None)
            ctrl_y: Control point Y offset (uses instance default if None)
            
        Returns:
            Command string in format: "km.move(x,y,segments,ctrl_x,ctrl_y)"
        """
        seg = int(segments if segments is not None else self.segments)
        cx = int(ctrl_x if ctrl_x is not None else self.ctrl_x)
        cy = int(ctrl_y if ctrl_y is not None else self.ctrl_y)
        
        return f"km.move({int(dx)},{int(dy)},{seg},{cx},{cy})"
    
    def get_movement_deltas(
        self,
        dx: float,
        dy: float,
        segments: Optional[int] = None,
        ctrl_x: Optional[float] = None,
        ctrl_y: Optional[float] = None
    ) -> List[Tuple[float, float]]:
        """
        Get incremental movement deltas for Bezier curve.
        
        Args:
            dx: Target X movement
            dy: Target Y movement
            segments: Number of segments (uses instance default if None)
            ctrl_x: Control point X offset (uses instance default if None)
            ctrl_y: Control point Y offset (uses instance default if None)
            
        Returns:
            List of (delta_x, delta_y) tuples for each movement step
        """
        seg = int(segments if segments is not None else self.segments)
        cx = float(ctrl_x if ctrl_x is not None else self.ctrl_x)
        cy = float(ctrl_y if ctrl_y is not None else self.ctrl_y)
        
        return calculate_bezier_movement_deltas(dx, dy, cx, cy, seg)
    
    def update_parameters(
        self,
        segments: Optional[int] = None,
        ctrl_x: Optional[float] = None,
        ctrl_y: Optional[float] = None
    ):
        """
        Update Bezier movement parameters.
        
        Args:
            segments: New number of segments
            ctrl_x: New control point X offset
            ctrl_y: New control point Y offset
        """
        if segments is not None:
            self.segments = max(0, int(segments))
        if ctrl_x is not None:
            self.ctrl_x = float(ctrl_x)
        if ctrl_y is not None:
            self.ctrl_y = float(ctrl_y)
