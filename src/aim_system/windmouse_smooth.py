import math
import random
import time
import numpy as np

class WindMouse:
    """
    WindMouse algorithm for human-like mouse movement.
    Based on the original WindMouse algorithm with enhancements for smoothness.
    """
    
    def __init__(self):
        self.last_x = 0
        self.last_y = 0
        self.last_time = time.time()
        
    def wind_mouse(self, start_x, start_y, dest_x, dest_y, gravity, wind, 
                   min_wait, max_wait, max_step, target_area, distance_threshold=50.0):
        """
        Generate human-like mouse movement path from start to destination.
        
        Args:
            distance_threshold: Distance threshold where behavior changes.
                               Below this distance, movement becomes more precise and controlled.
        """
        current_x, current_y = float(start_x), float(start_y)
        velocity_x = velocity_y = wind_x = wind_y = 0.0
        path = []
        carry_x = 0.0
        carry_y = 0.0
        total_time = 0.0 
        # Pre-calculate constants for performance
        sqrt3 = math.sqrt(3)
        drag_factor = 0.995
        
        while True:
            # Calculate distance to target (optimized)
            dx_to_target = dest_x - current_x
            dy_to_target = dest_y - current_y
            distance_squared = dx_to_target * dx_to_target + dy_to_target * dy_to_target
            
            # Break if we're close enough to target
            if distance_squared < target_area * target_area:
                break
            
            # Calculate distance for threshold check
            distance = math.sqrt(distance_squared) if distance_squared > 1 else 0.0
            
            # Dynamic adjustment based on distance threshold
            if distance_threshold > 0 and distance < distance_threshold:
                # Below threshold: reduce wind (less randomness), increase gravity (more precise)
                effective_wind = wind * 0.3  # Reduce randomness for precision
                effective_gravity = gravity * 1.5  # Increase lock-on strength
            else:
                # Above threshold: normal behavior
                effective_wind = wind
                effective_gravity = gravity
                
            # Update wind (random force) - optimized
            wind_x = wind_x / sqrt3 + (random.random() - 0.5) * effective_wind * 2
            wind_y = wind_y / sqrt3 + (random.random() - 0.5) * effective_wind * 2
            
            # Calculate gravitational pull towards target - optimized
            if distance_squared > 1:
                gravity_x = effective_gravity * dx_to_target / distance
                gravity_y = effective_gravity * dy_to_target / distance
            else:
                gravity_x = gravity_y = 0
                
            # Update velocity with wind and gravity
            velocity_x += wind_x + gravity_x
            velocity_y += wind_y + gravity_y
            
            # Apply drag/friction
            velocity_x *= drag_factor
            velocity_y *= drag_factor
            
            # Limit maximum step size - optimized
            step_size_squared = velocity_x * velocity_x + velocity_y * velocity_y
            if step_size_squared > max_step * max_step:
                scale = max_step / math.sqrt(step_size_squared)
                velocity_x *= scale
                velocity_y *= scale
            
            # Calculate next position
            next_x = current_x + velocity_x
            next_y = current_y + velocity_y

            
            # Calculate delay for this step (human-like timing)
            delay = random.uniform(min_wait, max_wait)

            carry_x += (next_x - current_x)
            carry_y += (next_y - current_y)
            out_dx = int(round(carry_x))
            out_dy = int(round(carry_y))
            carry_x -= out_dx
            carry_y -= out_dy
            
            # Add to path
            if out_dx != 0 or out_dy != 0:
                path.append((out_dx, out_dy, delay))
            
            current_x, current_y = next_x, next_y
            total_time += delay
            
            # Safety break to prevent infinite loops - optimized limits
            if len(path) > 100:  # Further reduced for better performance
                break
            if total_time > 0.25:  # Reduced time budget for faster response
                break
        return path

class SmoothAiming:
    """
    Advanced smooth aiming system with multiple humanization techniques.
    """
    
    def __init__(self):
        self.windmouse = WindMouse()
        self.last_target = None
        self.target_history = []
        self.aim_fatigue = 0.0
        self.reaction_delay = 0.0
        self.last_reaction_time = 0
        
    def calculate_smooth_path(self, dx, dy, config):
        """
        Calculate smooth movement path to target using configured settings.
        """
        current_time = time.time()
        
        # Skip if movement is too small
        distance = math.sqrt(dx**2 + dy**2)
        if distance < 2:
            return []
        
        # Human reaction time simulation
        if self.last_target is None or self._target_changed(dx, dy):
            self.reaction_delay = random.uniform(config.smooth_reaction_min, config.smooth_reaction_max)
            self.last_target = (dx, dy)
            self.last_reaction_time = current_time
            # New target detected, applying reaction delay
            
        # Check if we're still in reaction delay
        if current_time - self.last_reaction_time < self.reaction_delay:
            return []
        
        # Dynamic speed based on distance (closer = slower)
        if distance < config.smooth_close_range:
            speed_multiplier = config.smooth_close_speed
        elif distance > config.smooth_far_range:
            speed_multiplier = config.smooth_far_speed
        else:
            # Interpolate between close and far speeds
            ratio = (distance - config.smooth_close_range) / (config.smooth_far_range - config.smooth_close_range)
            speed_multiplier = config.smooth_close_speed + ratio * (config.smooth_far_speed - config.smooth_close_speed)
        
        # Distance and speed calculated
        
        # Apply fatigue (longer aiming = more shaky)
        self.aim_fatigue = min(self.aim_fatigue + 0.01, 1.0)
        fatigue_shake = self.aim_fatigue * config.smooth_fatigue_effect
        
        # Calculate WindMouse parameters based on config
        gravity = config.smooth_gravity + random.uniform(-1, 1)
        wind = config.smooth_wind + fatigue_shake + random.uniform(-0.5, 0.5)
        
        # Dynamic step size based on distance and speed
        max_step = distance * speed_multiplier * config.smooth_max_step_ratio
        max_step = max(config.smooth_min_step, min(max_step, config.smooth_max_step))
        
        # Target area (stop when close enough)
        target_area = max(2, distance * config.smooth_target_area_ratio)
        
        # Get distance threshold from config (if available)
        distance_threshold = getattr(config, 'smooth_distance_threshold', 50.0)
        
        # WindMouse parameters calculated
        
        # Generate movement path
        path = self.windmouse.wind_mouse(
            0, 0, dx, dy,
            gravity=gravity,
            wind=wind,
            min_wait=config.smooth_min_delay,
            max_wait=config.smooth_max_delay,
            max_step=max_step,
            target_area=target_area,
            distance_threshold=distance_threshold
        )
        
        # Apply smoothing and filtering
        filtered_path = self._apply_smoothing_filters(path, config)
        # Movement path generated
        return filtered_path
    
    def _target_changed(self, dx, dy, threshold=10):
        """Check if target has changed significantly."""
        if self.last_target is None:
            return True
        
        last_dx, last_dy = self.last_target
        change = math.sqrt((dx - last_dx)**2 + (dy - last_dy)**2)
        return change > threshold
    
    def _apply_smoothing_filters(self, path, config):
        """Apply additional smoothing and humanization to the movement path."""
        if len(path) < 2:
            return path
        
        smoothed_path = []
        
        # Apply acceleration/deceleration curves
        for i, (dx, dy, delay) in enumerate(path):
            progress = i / len(path)
            
            # Ease-in-out curve for more natural acceleration
            if progress < 0.3:
                # Acceleration phase
                multiplier = self._ease_in(progress / 0.3) * config.smooth_acceleration
            elif progress > 0.7:
                # Deceleration phase  
                multiplier = self._ease_out((progress - 0.7) / 0.3) * config.smooth_deceleration
            else:
                # Constant speed phase
                multiplier = 1.0

            multiplier = max(multiplier, 0.6) # keep steps from collapsing too much

            # Apply micro-corrections and jitter
            if config.smooth_micro_corrections > 0 and random.random() < 0.1:
                dx += random.randint(-config.smooth_micro_corrections, config.smooth_micro_corrections)
                dy += random.randint(-config.smooth_micro_corrections, config.smooth_micro_corrections)
            
            # Scale movement
            final_dx = int(dx * multiplier)
            final_dy = int(dy * multiplier)
            
            # Add slight delay variation
            final_delay = delay * random.uniform(0.8, 1.2)
            
            if final_dx != 0 or final_dy != 0:  # Only add non-zero movements
                smoothed_path.append((final_dx, final_dy, final_delay))
        
        return smoothed_path
    
    def _ease_in(self, t):
        """Ease-in function for smooth acceleration."""
        return t * t
    
    def _ease_out(self, t):
        """Ease-out function for smooth deceleration."""
        return 1 - (1 - t) * (1 - t)
    
    def reset_fatigue(self):
        """Reset aim fatigue (call when not aiming for a while)."""
        self.aim_fatigue = max(0, self.aim_fatigue - 0.1)

# Global smooth aiming instance
smooth_aimer = SmoothAiming()