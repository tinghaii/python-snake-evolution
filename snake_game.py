import pygame
import random
import sys
import math
import os

# Initialize Pygame
pygame.init()

# Initialize pygame mixer with specific settings
pygame.mixer.quit()  # Quit any existing mixer
pygame.mixer.init(44100, -16, 2, 2048)  # Increased buffer size for better sound handling
pygame.mixer.set_num_channels(8)  # Ensure we have enough channels

# Initialize global sound variables
SOUND_ENABLED = False  # Initialize to False by default
SOUNDS = {}
SOUND_ENABLED = True

# Load sound files
sound_files = {
    'background': 'assets/background.wav',
    'evolve': 'assets/evolve.wav',
    'eat': 'assets/eat.wav',
    'ice': 'assets/ice.wav',
    'menu': 'assets/menu.wav',
    'die': 'assets/die.wav'
}

try:
    for sound_name, file_path in sound_files.items():
        if not os.path.exists(file_path):
            continue
        try:
            sound = pygame.mixer.Sound(file_path)
            SOUNDS[sound_name] = sound
        except Exception:
            SOUND_ENABLED = False
            break

    if len(SOUNDS) < len(sound_files):
        SOUND_ENABLED = False

except Exception:
    SOUNDS = {}
    SOUND_ENABLED = False

# Constants
WINDOW_SIZE = 800
GRID_SIZE = 30
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BACKGROUND_COLOR = (255, 255, 255)  # White background
SNAKE_COLOR = (24, 128, 56)  # Google green
SNAKE_HEAD_COLOR = (21, 115, 50)  # Slightly darker green
FOOD_COLOR = (220, 53, 34)  # Google red
GRID_COLOR = (240, 240, 240)  # Light grey for grid
SCORE_COLOR = (95, 99, 104)  # Google grey

# Add new constants
MENU_BG_COLOR = (245, 245, 245)
BUTTON_COLOR = (26, 115, 232)
BUTTON_HOVER_COLOR = (66, 133, 244)
BUTTON_TEXT_COLOR = WHITE
PARTICLE_COLORS = {
    'apple': [(255, 99, 71), (255, 69, 0)],
    'banana': [(255, 215, 0), (255, 193, 7)],
    'orange': [(255, 140, 0), (255, 152, 0)],
    'berry': [(186, 85, 211), (156, 39, 176)],
    'kiwi': [(139, 195, 74), (119, 175, 54)],
    'poison': [(58, 66, 71), (38, 46, 51)],
    'ice_cream': [(240, 248, 255), (230, 230, 250)]
}

# Add new constants
FRUITS = {
    'apple': {'color': (220, 53, 34), 'points': 1},      # Red apple
    'banana': {'color': (255, 193, 7), 'points': 2},     # Yellow banana
    'orange': {'color': (255, 152, 0), 'points': 3},     # Orange
    'berry': {'color': (156, 39, 176), 'points': 5},     # Purple berry
    'kiwi': {'color': (139, 195, 74), 'points': 4},      # Green kiwi
    'poison': {'color': (58, 66, 71), 'points': -3},     # Dark grey poison
    'ice_cream': {'color': (240, 248, 255), 'points': 6, 'speed_effect': 0.5}  # Special dragon evolution reward
}

# Update evolution stages with more detailed appearances
EVOLUTION_STAGES = {
    0: {
        'color': (24, 128, 56),    # Basic green
        'head_color': (21, 115, 50),
        'patterns': []  # Empty list for initial stage
    },
    10: {
        'color': (30, 144, 255),   # Blue stage
        'head_color': (25, 125, 225),
        'patterns': ['scales']  # First pattern
    },
    15: {
        'color': (255, 69, 0),     # Fire orange
        'head_color': (220, 53, 34),
        'patterns': ['scales', 'fire']  # Add fire effect
    },
    20: {
        'color': (218, 165, 32),   # Golden stage
        'head_color': (184, 134, 11),
        'patterns': ['scales', 'fire', 'golden_scales']
    },
    30: {
        'color': (138, 43, 226),   # Purple stage
        'head_color': (106, 90, 205),
        'patterns': ['scales', 'fire', 'golden_scales', 'textile']
    },
    35: {
        'color': (255, 215, 0),    # Golden with wings
        'head_color': (218, 165, 32),
        'patterns': ['scales', 'fire', 'golden_scales', 'textile', 'wings']
    },
    40: {
        'color': (70, 130, 180),   # Steel blue with feet
        'head_color': (95, 158, 160),
        'patterns': ['scales', 'fire', 'golden_scales', 'textile', 'wings', 'feet']
    },
    45: {
        'color': (178, 34, 34),    # Dragon form
        'head_color': (139, 0, 0),
        'patterns': ['scales', 'fire', 'golden_scales', 'textile', 'wings', 'feet', 'dragon']
    }
}

# Set up the display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()

def draw_gradient_background():
    # Replace gradient with clean white background and subtle grid
    screen.fill(BACKGROUND_COLOR)
    # Draw subtle grid lines
    for i in range(0, WINDOW_SIZE, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (i, 0), (i, WINDOW_SIZE))
        pygame.draw.line(screen, GRID_COLOR, (0, i), (WINDOW_SIZE, i))

def draw_rounded_rectangle(surface, color, rect, radius):
    x, y, width, height = rect
    pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, height))
    pygame.draw.rect(surface, color, (x, y + radius, width, height - 2*radius))
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius, y + height - radius), radius)

class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [(GRID_COUNT // 2, GRID_COUNT // 2)]
        self.direction = (1, 0)  # Start moving right
        self.color = SNAKE_COLOR
        self.head_color = SNAKE_HEAD_COLOR  # Initialize head_color
        self.score = 0
        self.radius = GRID_SIZE // 2 - 1
        self.speed = 1  # Grid cells per update
        self.glow_factor = 0
        self.glow_increasing = True
        self.growth_pending = 0  # For smoother growth animation
        self.evolution_stage = 0
        self.speed_reduction_timer = 0  # Timer for ice cream speed reduction effect
        self.update_colors()  # This will set both color and head_color based on initial stage

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        # Update speed reduction timer
        if self.speed_reduction_timer > 0:
            self.speed_reduction_timer -= 1
            if self.speed_reduction_timer == 0:
                self.speed = 1  # Restore normal speed

        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_COUNT, (cur[1] + y) % GRID_COUNT)
        
        if new in self.positions[3:]:
            return False
            
        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()

        if self.growth_pending > 0:
            self.length += 1
            self.growth_pending -= 1

        return True

    def reset(self):
        self.length = 3  # Start with length 3 instead of 1
        self.positions = [
            (GRID_COUNT // 2, GRID_COUNT // 2),
            (GRID_COUNT // 2 - 1, GRID_COUNT // 2),
            (GRID_COUNT // 2 - 2, GRID_COUNT // 2)
        ]
        self.direction = (1, 0)
        self.score = 0

    def check_evolution(self):
        # Find current evolution stage
        current_stage = 0
        #print(f"Checking evolution for score: {self.score}")  # Debug score check
        for score, colors in sorted(EVOLUTION_STAGES.items()):
            if self.score >= score:
                current_stage = score
                #print(f"Qualified for stage {score}")  # Debug stage qualification
        
        if current_stage != self.evolution_stage:
            #print(f"Evolution change detected: {self.evolution_stage} -> {current_stage}")  # Debug evolution change
            self.evolution_stage = current_stage
            self.update_colors()  # Update colors after evolution
            return True  # Return True to indicate evolution occurred
        return False  # Return False if no evolution occurred

    def update_colors(self):
        # Just update colors based on current evolution stage
        stage_colors = EVOLUTION_STAGES[self.evolution_stage]
        self.color = stage_colors['color']
        self.head_color = stage_colors['head_color']
        #print(f"New colors - Body: {self.color}, Head: {self.head_color}")  # Debug color change

    def render(self, surface):
        self.update_colors()
        
        # Draw snake body segments with accumulated patterns
        for i, p in enumerate(self.positions[1:], 1):
            x = p[0] * GRID_SIZE
            y = p[1] * GRID_SIZE
            rect = (x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2)
            
            # Draw base segment
            draw_rounded_rectangle(surface, self.color, rect, 4)
            
            # Add all patterns based on evolution stage
            patterns = EVOLUTION_STAGES[self.evolution_stage]['patterns']
            for pattern in patterns:
                if pattern == 'scales':
                    scale_color = (max(0, self.color[0]-30), max(0, self.color[1]-30), max(0, self.color[2]-30))
                    for dx in [-2, 2]:
                        for dy in [-2, 2]:
                            pygame.draw.circle(surface, scale_color, 
                                            (x + GRID_SIZE//2 + dx, y + GRID_SIZE//2 + dy), 2)
                
                elif pattern == 'fire':
                    # Draw flame effect
                    flame_colors = [(255, 69, 0), (255, 140, 0), (255, 215, 0)]  # Red, Orange, Yellow
                    flame_offset = math.sin(pygame.time.get_ticks() * 0.01 + i * 0.5) * 2  # Animated flame
                    
                    # Get the snake's direction
                    direction = self.direction if i == 0 else (0, 0)
                    dx, dy = direction
                    
                    for j, flame_color in enumerate(flame_colors):
                        if dx != 0:  # Moving horizontally
                            # Draw flames on both sides
                            flame_points_top = [
                                (x + GRID_SIZE//2, y - 3 - j*2 + flame_offset),
                                (x + GRID_SIZE//2 - 3, y + 1 - j*2 + flame_offset),
                                (x + GRID_SIZE//2 + 3, y + 1 - j*2 + flame_offset),
                            ]
                            flame_points_bottom = [
                                (x + GRID_SIZE//2, y + GRID_SIZE + 3 + j*2 - flame_offset),
                                (x + GRID_SIZE//2 - 3, y + GRID_SIZE - 1 + j*2 - flame_offset),
                                (x + GRID_SIZE//2 + 3, y + GRID_SIZE - 1 + j*2 - flame_offset),
                            ]
                            pygame.draw.polygon(surface, flame_color, flame_points_top)
                            pygame.draw.polygon(surface, flame_color, flame_points_bottom)
                        else:  # Moving vertically or not moving
                            flame_points = [
                                (x + GRID_SIZE//2, y - 2 - j*2 + flame_offset),
                                (x + GRID_SIZE//2 - 3, y + 2 - j*2 + flame_offset),
                                (x + GRID_SIZE//2 + 3, y + 2 - j*2 + flame_offset),
                            ]
                            pygame.draw.polygon(surface, flame_color, flame_points)
                
                elif pattern == 'golden_scales':
                    highlight = (255, 223, 0)
                    shadow = (160, 120, 0)
                    for dx in [-3, 0, 3]:
                        pygame.draw.circle(surface, highlight, 
                                        (x + GRID_SIZE//2 + dx, y + GRID_SIZE//2), 2)
                        pygame.draw.circle(surface, shadow, 
                                        (x + GRID_SIZE//2 + dx, y + GRID_SIZE//2 + 2), 2)
                
                elif pattern == 'textile':
                    pattern_color = (max(0, self.color[0]-20), max(0, self.color[1]-20), max(0, self.color[2]-20))
                    for dx in range(2, GRID_SIZE-2, 4):
                        pygame.draw.line(surface, pattern_color,
                                       (x + dx, y + 2),
                                       (x + dx, y + GRID_SIZE - 2), 1)
                
                elif pattern == 'wings':
                    if i % 4 == 0:
                        wing_color = (255, 223, 0)
                        wing_points = [
                            (x - 4, y + GRID_SIZE//2),
                            (x - 8, y + 2),
                            (x - 4, y + GRID_SIZE - 2)
                        ]
                        pygame.draw.polygon(surface, wing_color, wing_points)
                        wing_points = [
                            (x + GRID_SIZE + 4, y + GRID_SIZE//2),
                            (x + GRID_SIZE + 8, y + 2),
                            (x + GRID_SIZE + 4, y + GRID_SIZE - 2)
                        ]
                        pygame.draw.polygon(surface, wing_color, wing_points)
                
                elif pattern == 'feet':
                    if i % 6 == 0:
                        foot_color = (95, 158, 160)
                        pygame.draw.circle(surface, foot_color,
                                        (x + GRID_SIZE//2 - 6, y + GRID_SIZE + 2), 3)
                        pygame.draw.circle(surface, foot_color,
                                        (x + GRID_SIZE//2 + 6, y + GRID_SIZE + 2), 3)
                
                elif pattern == 'dragon':
                    spike_color = (139, 0, 0)
                    for dx in [-4, 0, 4]:
                        pygame.draw.polygon(surface, spike_color, [
                            (x + GRID_SIZE//2 + dx, y - 2),
                            (x + GRID_SIZE//2 + dx - 2, y + 4),
                            (x + GRID_SIZE//2 + dx + 2, y + 4)
                        ])
                    scale_color = (178, 34, 34)
                    for dx in [-2, 2]:
                        for dy in [-2, 2]:
                            pygame.draw.circle(surface, scale_color,
                                            (x + GRID_SIZE//2 + dx, y + GRID_SIZE//2 + dy), 2)

        # Draw enhanced dragon head
        head = self.positions[0]
        head_x = head[0] * GRID_SIZE
        head_y = head[1] * GRID_SIZE

        # Special dragon head rendering when fully evolved
        if self.evolution_stage >= 45:  # Dragon form
            # Determine head direction and orientation
            if self.direction == (1, 0):  # RIGHT
                self.draw_dragon_head(surface, head_x, head_y, 0)
            elif self.direction == (-1, 0):  # LEFT
                self.draw_dragon_head(surface, head_x, head_y, 180)
            elif self.direction == (0, -1):  # UP
                self.draw_dragon_head(surface, head_x, head_y, 270)
            else:  # DOWN
                self.draw_dragon_head(surface, head_x, head_y, 90)
        else:
            # Regular head rendering for other evolution stages
            head_rect = (head_x + 1, head_y + 1, GRID_SIZE - 2, GRID_SIZE - 2)
            draw_rounded_rectangle(surface, self.head_color, head_rect, 4)

        # Enhanced head features based on evolution
        if self.evolution_stage >= 40:  # Add horns for advanced stages
            horn_color = (139, 0, 0) if self.evolution_stage >= 60 else (218, 165, 32)
            pygame.draw.polygon(surface, horn_color, [
                (head_x + 2, head_y),
                (head_x + 6, head_y - 4),
                (head_x + 4, head_y + 2)
            ])
            pygame.draw.polygon(surface, horn_color, [
                (head_x + GRID_SIZE - 2, head_y),
                (head_x + GRID_SIZE - 6, head_y - 4),
                (head_x + GRID_SIZE - 4, head_y + 2)
            ])

        # Draw eyes with glow effect for higher stages
        eye_radius = 2
        eye_color = WHITE if self.evolution_stage < 60 else (255, 0, 0)  # Red eyes for dragon
        
        if self.direction == (1, 0):  # RIGHT
            left_eye_pos = (head_x + GRID_SIZE - 6, head_y + 7)
            right_eye_pos = (head_x + GRID_SIZE - 6, head_y + GRID_SIZE - 7)
        elif self.direction == (-1, 0):  # LEFT
            left_eye_pos = (head_x + 6, head_y + 7)
            right_eye_pos = (head_x + 6, head_y + GRID_SIZE - 7)
        elif self.direction == (0, -1):  # UP
            left_eye_pos = (head_x + 7, head_y + 6)
            right_eye_pos = (head_x + GRID_SIZE - 7, head_y + 6)
        else:  # DOWN
            left_eye_pos = (head_x + 7, head_y + GRID_SIZE - 6)
            right_eye_pos = (head_x + GRID_SIZE - 7, head_y + GRID_SIZE - 6)

        # Draw glowing eyes for advanced stages
        if self.evolution_stage >= 30:
            glow_radius = eye_radius + 1
            glow_color = (255, 255, 150) if self.evolution_stage < 60 else (255, 100, 100)
            pygame.draw.circle(surface, glow_color, left_eye_pos, glow_radius)
            pygame.draw.circle(surface, glow_color, right_eye_pos, glow_radius)

        pygame.draw.circle(surface, eye_color, left_eye_pos, eye_radius)
        pygame.draw.circle(surface, eye_color, right_eye_pos, eye_radius)

    def draw_dragon_head(self, surface, x, y, angle):
        # Enhanced colors
        main_color = (178, 34, 34)  # Dark red
        accent_color = (255, 140, 0)  # Orange
        horn_color = (139, 69, 19)  # Brown
        scale_color = (139, 0, 0)  # Darker red for scales
        
        center_x = x + GRID_SIZE // 2
        center_y = y + GRID_SIZE // 2

        def rotate_point(px, py, cx, cy, angle_deg):
            angle_rad = math.radians(angle_deg)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            dx = px - cx
            dy = py - cy
            return (
                cx + dx * cos_a - dy * sin_a,
                cy + dx * sin_a + dy * cos_a
            )

        # Larger, more detailed head shape
        head_points = [
            (x - 4, y + GRID_SIZE//2),      # Left middle
            (x + 6, y - 4),                 # Top curve 1
            (x + GRID_SIZE//2, y - 6),      # Top curve 2
            (x + GRID_SIZE + 6, y + GRID_SIZE//2),  # Snout tip
            (x + GRID_SIZE//2, y + GRID_SIZE + 6),  # Bottom curve 2
            (x + 6, y + GRID_SIZE + 4)      # Bottom curve 1
        ]
        
        # Rotate and draw main head
        rotated_head = [rotate_point(px, py, center_x, center_y, angle) for px, py in head_points]
        pygame.draw.polygon(surface, main_color, rotated_head)

        # Add scales pattern
        scale_positions = [
            (x + 8, y + 4),
            (x + 16, y + 4),
            (x + 24, y + 4),
            (x + 8, y + GRID_SIZE - 4),
            (x + 16, y + GRID_SIZE - 4),
            (x + 24, y + GRID_SIZE - 4)
        ]
        
        for scale_pos in scale_positions:
            rotated_scale = rotate_point(scale_pos[0], scale_pos[1], center_x, center_y, angle)
            pygame.draw.circle(surface, scale_color, rotated_scale, 3)

        # Enhanced horns (more curved)
        horn_points1 = [
            (x + 4, y - 2),
            (x + 10, y - 12),
            (x + 16, y - 8),
            (x + 12, y - 2)
        ]
        horn_points2 = [
            (x + 14, y - 2),
            (x + 20, y - 10),
            (x + 26, y - 6),
            (x + 22, y - 2)
        ]
        
        # Draw horns with shading
        for horn_points in [horn_points1, horn_points2]:
            rotated_horn = [rotate_point(px, py, center_x, center_y, angle) for px, py in horn_points]
            pygame.draw.polygon(surface, horn_color, rotated_horn)
            # Add horn highlights
            pygame.draw.line(surface, (139, 101, 8), 
                           rotated_horn[0], rotated_horn[1], 2)

        # Enhanced snout with nostrils
        snout_points = [
            (x + GRID_SIZE - 2, y + GRID_SIZE//2 - 6),
            (x + GRID_SIZE + 8, y + GRID_SIZE//2),
            (x + GRID_SIZE - 2, y + GRID_SIZE//2 + 6)
        ]
        rotated_snout = [rotate_point(px, py, center_x, center_y, angle) for px, py in snout_points]
        pygame.draw.polygon(surface, accent_color, rotated_snout)

        # Improved eyes with better glow effect
        eye_radius = 3
        glow_radius = 5
        for eye_offset in [(6, -4), (6, 4)]:
            eye_pos = rotate_point(x + GRID_SIZE - 8, y + GRID_SIZE//2 + eye_offset[1], 
                                 center_x, center_y, angle)
            
            # Multiple layers of glow
            for r in range(glow_radius, eye_radius-1, -1):
                glow_alpha = int(255 * (r/glow_radius))
                glow_surface = pygame.Surface((r*2+1, r*2+1), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*accent_color, glow_alpha), 
                                (r+1, r+1), r)
                surface.blit(glow_surface, 
                           (eye_pos[0]-r, eye_pos[1]-r))
            
            # Main eye
            pygame.draw.circle(surface, (255, 0, 0), eye_pos, eye_radius)
            # Eye shine
            pygame.draw.circle(surface, (255, 255, 255), 
                             (eye_pos[0]-1, eye_pos[1]-1), 1)

        # Add more detailed teeth
        teeth_color = (255, 250, 250)
        teeth_positions = [
            (x + GRID_SIZE - 2, y + GRID_SIZE//2 - 4),
            (x + GRID_SIZE - 2, y + GRID_SIZE//2),
            (x + GRID_SIZE - 2, y + GRID_SIZE//2 + 4)
        ]
        
        for tooth_pos in teeth_positions:
            tooth_points = [
                tooth_pos,
                (tooth_pos[0] + 4, tooth_pos[1]),
                (tooth_pos[0] + 2, tooth_pos[1] + 2)
            ]
            rotated_tooth = [rotate_point(px, py, center_x, center_y, angle) 
                           for px, py in tooth_points]
            pygame.draw.polygon(surface, teeth_color, rotated_tooth)

    def grow(self, amount):
        self.growth_pending += amount

    def apply_speed_reduction(self):
        self.speed = max(1, math.ceil(self.speed * 0.2))  # Reduce speed to 20% and round up
        self.speed_reduction_timer = 100  # 10 seconds at normal game speed (10 FPS)

class Food:
    def __init__(self, game):
        self.game = game
        self.positions = []  # List of (position, fruit_type) tuples
        self.poison_timer = 0
        self.poison_duration = 100  # Duration in frames (10 seconds at normal speed)
        self.radius = GRID_SIZE // 2 - 2
        self.randomize()

    def randomize(self):
        # Remove poison if it exists
        self.positions = [pos for pos in self.positions if pos[1] != 'poison']
        
        # Always ensure at least one regular food exists
        if not self.positions:
            self.add_food('apple')

        # 25% chance to spawn poison (increased from 10%)
        if random.random() < 0.25:
            self.add_food('poison')
            self.poison_timer = self.poison_duration

    def add_food(self, fruit_type):
        # Find valid position not on snake or other food
        while True:
            new_pos = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
            if (new_pos not in self.game.snake.positions and 
                new_pos not in [p[0] for p in self.positions]):
                break
        
        if fruit_type == 'poison':
            self.positions.append((new_pos, 'poison'))
        else:
            # Weighted random choice for regular fruits including ice cream
            weights = [0.35, 0.15, 0.15, 0.1, 0.1, 0.15]  # Including ice cream
            fruit_type = random.choices(
                ['apple', 'banana', 'orange', 'berry', 'kiwi', 'ice_cream'], 
                weights=weights
            )[0]
            self.positions.append((new_pos, fruit_type))

    def update(self):
        # Update poison timer
        if any(fruit_type == 'poison' for _, fruit_type in self.positions):
            self.poison_timer -= 1
            if self.poison_timer <= 0:
                # Remove poison
                self.positions = [pos for pos in self.positions if pos[1] != 'poison']

    def render(self, surface):
        for position, fruit_type in self.positions:
            x = position[0] * GRID_SIZE + GRID_SIZE // 2
            y = position[1] * GRID_SIZE + GRID_SIZE // 2
            fruit_color = FRUITS[fruit_type]['color']

            if fruit_type == 'apple':
                # Improved apple with gradient and better shine
                darker_color = (max(0, fruit_color[0]-40), max(0, fruit_color[1]-40), max(0, fruit_color[2]-40))
                # Main apple body
                pygame.draw.circle(surface, fruit_color, (x, y), self.radius)
                # Bottom shadow
                pygame.draw.circle(surface, darker_color, (x, y+2), self.radius-1)
                # Top shine
                shine_pos = (x - self.radius//3, y - self.radius//3)
                pygame.draw.ellipse(surface, (255, 255, 255, 180), 
                                  (shine_pos[0]-2, shine_pos[1]-1, 5, 3))
                # Stem
                stem_start = (x, y - self.radius + 1)
                stem_end = (x + 2, y - self.radius - 3)
                pygame.draw.line(surface, (83, 40, 30), stem_start, stem_end, 2)
                # Leaf with gradient
                leaf_points = [(x + 2, y - self.radius - 2),
                             (x + 7, y - self.radius - 4),
                             (x + 4, y - self.radius)]
                pygame.draw.polygon(surface, (67, 160, 71), leaf_points)
                pygame.draw.polygon(surface, (45, 136, 45), 
                                  [(x + 2, y - self.radius - 2),
                                   (x + 5, y - self.radius - 3),
                                   (x + 4, y - self.radius)])

            elif fruit_type == 'banana':
                # Improved banana with better curve and gradient
                lighter_color = (min(255, fruit_color[0]+40), min(255, fruit_color[1]+40), min(255, fruit_color[2]+40))
                darker_color = (max(0, fruit_color[0]-40), max(0, fruit_color[1]-40), max(0, fruit_color[2]-40))
                
                # Main banana shape
                points = [
                    (x - 8, y + 2),
                    (x - 6, y - 4),
                    (x + 2, y - 6),
                    (x + 8, y - 2),
                    (x + 6, y + 4),
                    (x - 2, y + 6),
                ]
                pygame.draw.polygon(surface, fruit_color, points)
                # Gradient effect
                pygame.draw.line(surface, lighter_color, (x - 4, y - 2), (x + 4, y + 2), 3)
                # Edges
                pygame.draw.lines(surface, darker_color, True, points, 1)

            elif fruit_type == 'orange':
                # Improved orange with better texture and gradient
                lighter_color = (min(255, fruit_color[0]+40), min(255, fruit_color[1]+40), min(255, fruit_color[2]+40))
                
                # Main orange body
                pygame.draw.circle(surface, fruit_color, (x, y), self.radius)
                # Texture pattern
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    length = self.radius - 2
                    dot_x = x + math.cos(rad) * length
                    dot_y = y + math.sin(rad) * length
                    pygame.draw.circle(surface, lighter_color, (dot_x, dot_y), 1)
                # Shine
                shine_pos = (x - self.radius//3, y - self.radius//3)
                pygame.draw.ellipse(surface, (255, 255, 255, 180), 
                                  (shine_pos[0]-2, shine_pos[1]-1, 5, 3))

            elif fruit_type == 'berry':
                # Improved berry cluster with better shading
                positions = [(0, 0), (-3, -3), (3, -3), (-2, 2), (2, 2)]
                darker_color = (max(0, fruit_color[0]-40), max(0, fruit_color[1]-40), max(0, fruit_color[2]-40))
                
                # Draw berries with shading
                for dx, dy in positions:
                    pygame.draw.circle(surface, fruit_color, (x + dx, y + dy), self.radius - 2)
                    pygame.draw.circle(surface, darker_color, (x + dx, y + dy + 1), self.radius - 3)
                    # Add shine to each berry
                    shine_x = x + dx - 1
                    shine_y = y + dy - 1
                    pygame.draw.circle(surface, (255, 255, 255, 180), (shine_x, shine_y), 1)

            elif fruit_type == 'kiwi':
                # Improved kiwi with better texture and gradient
                darker_color = (max(0, fruit_color[0]-40), max(0, fruit_color[1]-40), max(0, fruit_color[2]-40))
                
                # Main kiwi body
                pygame.draw.circle(surface, fruit_color, (x, y), self.radius)
                pygame.draw.circle(surface, darker_color, (x, y+1), self.radius-1)
                
                # Add more detailed seed pattern
                for _ in range(8):
                    seed_x = x + random.randint(-self.radius+3, self.radius-3)
                    seed_y = y + random.randint(-self.radius+3, self.radius-3)
                    # Draw seed with shadow
                    pygame.draw.circle(surface, (0, 0, 0), (seed_x+1, seed_y+1), 1)
                    pygame.draw.circle(surface, (20, 20, 20), (seed_x, seed_y), 1)

            elif fruit_type == 'poison':
                # Improved poison bottle with better shading
                darker_color = (max(0, fruit_color[0]-40), max(0, fruit_color[1]-40), max(0, fruit_color[2]-40))
                
                # Draw timer bar for poison
                if self.poison_timer > 0:
                    timer_width = (self.poison_timer / self.poison_duration) * GRID_SIZE
                    timer_rect = pygame.Rect(x - GRID_SIZE//2, y - GRID_SIZE, timer_width, 2)
                    pygame.draw.rect(surface, (255, 0, 0), timer_rect)
                
                # Bottle body with gradient
                bottle_points = [
                    (x - 6, y + 6),
                    (x - 6, y - 2),
                    (x - 4, y - 4),
                    (x + 4, y - 4),
                    (x + 6, y - 2),
                    (x + 6, y + 6),
                ]
                pygame.draw.polygon(surface, fruit_color, bottle_points)
                pygame.draw.polygon(surface, darker_color, 
                                  [(p[0], p[1]+1) for p in bottle_points])
                
                # Bottle neck with gradient
                pygame.draw.rect(surface, fruit_color, (x - 2, y - 6, 4, 3))
                pygame.draw.rect(surface, darker_color, (x - 2, y - 5, 4, 2))
                
                # Improved skull symbol
                pygame.draw.circle(surface, (255, 255, 255), (x, y), 3)
                pygame.draw.circle(surface, (255, 255, 255), (x - 2, y - 1), 1)
                pygame.draw.circle(surface, (255, 255, 255), (x + 2, y - 1), 1)
                # Add crossbones
                pygame.draw.line(surface, (255, 255, 255), (x - 3, y + 3), (x + 3, y + 5), 1)
                pygame.draw.line(surface, (255, 255, 255), (x + 3, y + 3), (x - 3, y + 5), 1)

            elif fruit_type == 'ice_cream':
                # Draw ice cream cone
                cone_color = (210, 180, 140)  # Tan color for cone
                ice_color = (240, 248, 255)   # White for ice cream
                
                # Draw cone
                cone_points = [
                    (x, y + self.radius),
                    (x - self.radius, y - self.radius),
                    (x + self.radius, y - self.radius)
                ]
                pygame.draw.polygon(surface, cone_color, cone_points)
                
                # Draw ice cream scoops
                pygame.draw.circle(surface, ice_color, (x, y - self.radius), self.radius)
                pygame.draw.circle(surface, (255, 255, 255), 
                                (x - 2, y - self.radius - 2), self.radius // 3)  # Highlight

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = (random.uniform(-2, 2), random.uniform(-2, 2))
        self.lifetime = 20
        self.size = random.randint(2, 4)

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.lifetime -= 1
        self.size = max(0, self.size - 0.1)

    def render(self, surface):
       # Calculate alpha as a percentage of lifetime but clamp it within the valid range
        alpha = max(0, min(255, int(255 * (self.lifetime / 20))))
        # Create a temporary surface for the particle with alpha
        particle_surface = pygame.Surface((int(self.size * 2 + 1), int(self.size * 2 + 1)), pygame.SRCALPHA)   
       # Fix: Clamp color values within the valid range
        color_with_alpha = (
            max(0, min(255, int(self.color[0]))),
            max(0, min(255, int(self.color[1]))),
            max(0, min(255, int(self.color[2]))),
            alpha
        )
        #print(f"Rendering particle with color: {color_with_alpha}")
        # Draw the circle with the properly formatted color
        pygame.draw.circle(particle_surface, color_with_alpha, 
                         (int(self.size + 1), int(self.size + 1)), int(self.size))
        # Blit the temporary surface onto the main surface
        surface.blit(particle_surface, 
                    (int(self.x - self.size), int(self.y - self.size)))
       
class Button:
    def __init__(self, x, y, width, height, text, action, value=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.value = value
        self.is_hovered = False

    def render(self, surface):
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class SnowParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = (random.uniform(-1, 1), random.uniform(1, 3))
        self.lifetime = 30
        self.size = random.randint(2, 4)
        self.color = (200, 200, 200)  # Light grey color for snow to be visible on white background

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.lifetime -= 1
        self.size = max(0, self.size - 0.05)

    def render(self, surface):
        alpha = int(255 * (self.lifetime / 30))
        particle_surface = pygame.Surface((int(self.size * 2 + 1), int(self.size * 2 + 1)), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (*self.color, alpha), 
                         (int(self.size + 1), int(self.size + 1)), int(self.size))
        surface.blit(particle_surface, 
                    (int(self.x - self.size), int(self.y - self.size)))

class Game:
    def __init__(self):
        global SOUND_ENABLED
        self.snake = Snake()
        self.food = Food(self)
        self.particles = []
        self.high_score = 0
        self.state = 'menu'
        self.base_speed = 10
        self.speed_multiplier = 1.0
        self.game_speed = self.base_speed
        self.setup_menu()

        # Load game over image
        try:
            self.game_over_img = pygame.image.load('assets/game_over.png')
            self.game_over_img = pygame.transform.scale(self.game_over_img, (300, 300))
        except:
            self.game_over_img = None

        # Initialize sound channels
        if SOUND_ENABLED:
            try:
                self.background_channel = pygame.mixer.Channel(0)
                self.effect_channel = pygame.mixer.Channel(1)
                self.evolution_channel = pygame.mixer.Channel(2)
                
                # Set volumes
                self.background_channel.set_volume(0.5)
                self.effect_channel.set_volume(1.0)
                self.evolution_channel.set_volume(1.0)
                
                # Play menu sound initially
                if 'menu' in SOUNDS:
                    self.effect_channel.play(SOUNDS['menu'])
            except Exception as e:
                print(f"Error initializing sound channels: {e}")
                SOUND_ENABLED = False

        self.snow_particles = []
        self.ice_cream_active = False
        self.ice_cream_timer = 0
        self.ice_cream_duration = 300  # 5 seconds at 60 FPS
        self.original_speed = 10  # Store original speed
        self.slowed_speed = 5     # Slowed speed when ice cream is active
        self.game_speed = self.original_speed  # Initialize game speed

    def handle_collision(self, position, fruit_type):
        if fruit_type == 'ice_cream':
            self.ice_cream_active = True
            self.ice_cream_timer = self.ice_cream_duration
            self.game_speed = self.slowed_speed  # Reduce game speed
            self.snake.speed = self.slowed_speed  # Reduce snake speed
            if SOUND_ENABLED and 'ice' in SOUNDS:
                self.effect_channel.play(SOUNDS['ice'])
            # Create snow particles at the ice cream location
            for _ in range(20):
                self.snow_particles.append(SnowParticle(
                    position[0] * GRID_SIZE + GRID_SIZE // 2,
                    position[1] * GRID_SIZE + GRID_SIZE // 2
                ))
        self.snake.grow(FRUITS[fruit_type]['points'])
        self.snake.score += FRUITS[fruit_type]['points']
        # Create particles for the eaten fruit
        if fruit_type in PARTICLE_COLORS:
            for _ in range(10):
                particle_color = random.choice(PARTICLE_COLORS[fruit_type])
                x = position[0] * GRID_SIZE + GRID_SIZE // 2
                y = position[1] * GRID_SIZE + GRID_SIZE // 2
                self.particles.append(Particle(x, y, particle_color))
        
        # Load game over image
        try:
            self.game_over_img = pygame.image.load('assets/game_over.png')
            self.game_over_img = pygame.transform.scale(self.game_over_img, (300, 300))
        except:
            #print("Could not load game over image")
            self.game_over_img = None
        
        # Initialize sound system with debug info
        print("\n=== Game Sound System Initialization ===")
        if SOUND_ENABLED:
            try:
                # Set up three separate channels
                self.background_channel = pygame.mixer.Channel(0)
                self.effect_channel = pygame.mixer.Channel(1)
                self.evolution_channel = pygame.mixer.Channel(2)
                
                # Set and verify volumes
                self.background_channel.set_volume(0.5)
                self.effect_channel.set_volume(1.0)
                self.evolution_channel.set_volume(1.0)
                
                print("Sound channels initialized:")
                print(f"Background channel volume: {self.background_channel.get_volume()}")
                print(f"Effect channel volume: {self.effect_channel.get_volume()}")
                print(f"Evolution channel volume: {self.evolution_channel.get_volume()}")
                
                # Only play menu sound initially since we start in menu state
                if 'menu' in SOUNDS:
                    self.effect_channel.play(SOUNDS['menu'])
                    print("Menu sound started successfully")
            except Exception as e:
                print(f"Error initializing game sound system: {type(e).__name__}, {str(e)}")
                SOUND_ENABLED = False

        print(f"Game sound enabled: {SOUND_ENABLED}")
        if SOUND_ENABLED:
            print(f"Available game sounds: {list(SOUNDS.keys())}")

    def setup_menu(self):
        center_x = WINDOW_SIZE // 2
        self.buttons = {
            'menu': [
                Button(center_x - 100, 250, 200, 50, "Start Game", lambda: self.start_game()),
                Button(center_x - 100, 320, 200, 50, "Very Slow", lambda: self.set_speed(0.5), 0.5),
                Button(center_x - 100, 380, 200, 50, "Normal", lambda: self.set_speed(1.0), 1.0),
                Button(center_x - 100, 440, 200, 50, "Fast", lambda: self.set_speed(1.5), 1.5)
            ],
            'game_over': [
                Button(center_x - 100, 250, 200, 50, "Play Again", lambda: self.start_game()),
                Button(center_x - 100, 320, 200, 50, "Menu", lambda: self.show_menu())
            ]
        }

    def set_speed(self, multiplier):
        self.speed_multiplier = multiplier
        self.game_speed = int(self.base_speed * multiplier)

    def start_game(self):
        self.snake = Snake()
        self.food = Food(self)
        self.particles = []
        self.state = 'playing'
        if SOUND_ENABLED:
            # Stop menu sound
            self.effect_channel.stop()
            # Start background music
            if 'background' in SOUNDS:
                self.background_channel.play(SOUNDS['background'], -1)

    def show_menu(self):
        self.state = 'menu'
        if SOUND_ENABLED:
            # Stop all sounds first
            self.background_channel.stop()
            self.effect_channel.stop()
            self.evolution_channel.stop()
            # Play menu sound if available
            if 'menu' in SOUNDS:
                self.effect_channel.play(SOUNDS['menu'])

    def update(self):
        if self.state == 'playing':
            # Update food (for poison timer)
            self.food.update()

            # Update particles
            self.particles = [p for p in self.particles if p.lifetime > 0]
            for particle in self.particles:
                particle.update()

            # Store previous evolution stage
            previous_stage = self.snake.evolution_stage

            # Update snake
            keys = pygame.key.get_pressed()
            direction = self.snake.direction
            if keys[pygame.K_UP] and direction != (0, 1):
                self.snake.direction = (0, -1)
            elif keys[pygame.K_DOWN] and direction != (0, -1):
                self.snake.direction = (0, 1)
            elif keys[pygame.K_LEFT] and direction != (1, 0):
                self.snake.direction = (-1, 0)
            elif keys[pygame.K_RIGHT] and direction != (-1, 0):
                self.snake.direction = (1, 0)

            if not self.snake.update():
                # Stop background music immediately
                if SOUND_ENABLED:
                    self.background_channel.stop()
                
                # Set game over state immediately to show the image
                self.state = 'game_over'
                if self.snake.score > self.high_score:
                    self.high_score = self.snake.score
                
                # Display game over image for 2 seconds
                if self.game_over_img:
                    screen.blit(self.game_over_img, 
                              (WINDOW_SIZE//2 - 150, WINDOW_SIZE//2 - 150))
                    pygame.display.flip()
                    pygame.time.wait(2000)
                
                # Play death sound and wait for it to finish
                if SOUND_ENABLED and 'die' in SOUNDS:
                    self.effect_channel.play(SOUNDS['die'])
                    pygame.time.wait(int(SOUNDS['die'].get_length() * 1000))
                
                # Play menu sound after death sound
                if SOUND_ENABLED and 'menu' in SOUNDS:
                    self.effect_channel.play(SOUNDS['menu'])
                return

            # Check if snake evolved
            if self.snake.check_evolution():  # Use the new check_evolution method
                if SOUND_ENABLED:
                    try:
                        if self.evolution_channel.get_busy():
                            self.evolution_channel.stop()
                        
                        if 'evolve' in SOUNDS:
                            evolve_sound = SOUNDS['evolve']
                            evolve_sound.set_volume(1.0)
                            self.evolution_channel.set_volume(1.0)
                            self.evolution_channel.play(evolve_sound)
                            
                            if self.background_channel.get_busy():
                                self.background_channel.set_volume(0.2)
                                restore_time = int(evolve_sound.get_length() * 1000)
                                pygame.time.set_timer(pygame.USEREVENT + 1, restore_time)
                    except Exception:
                        pass
                
                self.create_evolution_particles()
                
                # Spawn ice cream if evolved to dragon
                if self.snake.evolution_stage >= 45:
                    self.spawn_ice_cream()

            # Update ice cream effect
            if self.ice_cream_active:
                self.ice_cream_timer -= 1
                if self.ice_cream_timer <= 0:
                    self.ice_cream_active = False
                    self.game_speed = self.original_speed
                    self.snake.speed = self.original_speed
                    # Clear all snow particles when effect ends
                    self.snow_particles.clear()
                else:
                    # Create snow particles around the snake's body
                    for pos in self.snake.positions:
                        x = pos[0] * GRID_SIZE + GRID_SIZE // 2
                        y = pos[1] * GRID_SIZE + GRID_SIZE // 2
                        # Create snow particles in a circular pattern around each segment
                        for angle in range(0, 360, 45):  # Create 8 particles per segment
                            rad = math.radians(angle)
                            offset_x = math.cos(rad) * GRID_SIZE
                            offset_y = math.sin(rad) * GRID_SIZE
                            self.snow_particles.append(SnowParticle(
                                x + offset_x,
                                y + offset_y
                            ))

            # Update snow particles
            for particle in self.snow_particles[:]:
                particle.update()
                if particle.lifetime <= 0:
                    self.snow_particles.remove(particle)

            # Check for food collision
            head_pos = self.snake.get_head_position()
            for i, (food_pos, fruit_type) in enumerate(self.food.positions):
                if head_pos == food_pos:
                    if SOUND_ENABLED:
                        if fruit_type == 'ice_cream':
                            self.effect_channel.play(SOUNDS['ice'])
                        else:
                            self.effect_channel.play(SOUNDS['eat'])
                    
                    # Handle ice cream effect
                    if fruit_type == 'ice_cream':
                        self.ice_cream_active = True
                        self.ice_cream_timer = self.ice_cream_duration
                        self.game_speed = self.slowed_speed
                        self.snake.speed = self.slowed_speed
                        # Create initial snow particles at the ice cream location
                        for _ in range(20):
                            self.snow_particles.append(SnowParticle(
                                food_pos[0] * GRID_SIZE + GRID_SIZE // 2,
                                food_pos[1] * GRID_SIZE + GRID_SIZE // 2
                            ))
                    else:
                        # If eating non-ice cream food, clear ice cream effect
                        self.ice_cream_active = False
                        self.game_speed = self.original_speed
                        self.snake.speed = self.original_speed
                        self.snow_particles.clear()
                    
                    points = FRUITS[fruit_type]['points']
                    
                    # Handle poison differently
                    if fruit_type == 'poison':
                        self.snake.score = max(0, self.snake.score + points)
                        if self.snake.length > 3:
                            self.snake.length -= 1
                            self.snake.positions.pop()
                    else:
                        self.snake.score += points
                        self.snake.grow(points)
                    
                    # Remove eaten food
                    self.food.positions.pop(i)
                    
                    # Spawn new food if no regular food exists
                    if not any(f[1] != 'poison' for f in self.food.positions):
                        self.food.add_food('apple')
                    break

    def create_particles(self):
        # Find the last eaten food position
        for food_pos, fruit_type in self.food.positions:
            if food_pos == self.snake.get_head_position():
                x = food_pos[0] * GRID_SIZE + GRID_SIZE // 2
                y = food_pos[1] * GRID_SIZE + GRID_SIZE // 2
                colors = PARTICLE_COLORS[fruit_type]
                for _ in range(10):
                    color = random.choice(colors)
                    self.particles.append(Particle(x, y, color))
                break

    def create_flame_particles(self, x, y, base_color, count, size_range, speed_range):
        for _ in range(count):
            color = (
                min(255, base_color[0] + random.randint(-20, 20)),
                min(255, base_color[1] + random.randint(-20, 20)),
                min(255, base_color[2] + random.randint(-20, 20))
            )
            particle = Particle(x, y, color)
            particle.size = random.uniform(*size_range)
            particle.velocity = (
                random.uniform(*speed_range),
                random.uniform(*speed_range)
            )
            particle.lifetime = 30
            self.particles.append(particle)

    def create_evolution_particles(self):
        # Create more elaborate particles for evolution
        new_color = EVOLUTION_STAGES[self.snake.evolution_stage]['color']
        
        # Different particle effects for different stages
        if self.snake.evolution_stage >= 45:  # Dragon form
            particle_count = 20
            particle_size = (3, 6)
            particle_speed = (-3, 3)
        elif self.snake.evolution_stage >= 35:  # Wings
            particle_count = 15
            particle_size = (2, 5)
            particle_speed = (-2.5, 2.5)
        elif self.snake.evolution_stage >= 15:  # Yellow snake and above
            particle_count = 12
            particle_size = (2, 4)
            particle_speed = (-2.5, 2.5)
            # Create symmetric flame effects on both sides
            for pos in self.snake.positions:
                x = pos[0] * GRID_SIZE + GRID_SIZE // 2
                y = pos[1] * GRID_SIZE + GRID_SIZE // 2
                # Left side flames
                self.create_flame_particles(x - GRID_SIZE//2, y, new_color, particle_count//2, particle_size, particle_speed)
                # Right side flames
                self.create_flame_particles(x + GRID_SIZE//2, y, new_color, particle_count//2, particle_size, particle_speed)
            return
        else:
            particle_count = 10
            particle_size = (2, 4)
            particle_speed = (-2, 2)

        # Create particles along the entire snake body
        for pos in self.snake.positions:
            x = pos[0] * GRID_SIZE + GRID_SIZE // 2
            y = pos[1] * GRID_SIZE + GRID_SIZE // 2
            
            for _ in range(particle_count):
                color = (
                    min(255, new_color[0] + random.randint(-20, 20)),
                    min(255, new_color[1] + random.randint(-20, 20)),
                    min(255, new_color[2] + random.randint(-20, 20))
                )
                particle = Particle(x, y, color)
                particle.size = random.uniform(*particle_size)
                particle.velocity = (
                    random.uniform(*particle_speed),
                    random.uniform(*particle_speed)
                )
                particle.lifetime = 30  # Longer lifetime for evolution particles
                self.particles.append(particle)

    def spawn_ice_cream(self):
        # Spawn 10 ice creams when turning into dragon
        for _ in range(10):
            self.food.add_food('ice_cream')

    def render(self, screen):
        if self.state == 'menu':
            screen.fill(MENU_BG_COLOR)
            font = pygame.font.Font(None, 74)
            title = font.render("Snake Game", True, SCORE_COLOR)
            screen.blit(title, (WINDOW_SIZE//2 - title.get_width()//2, 100))
            for button in self.buttons['menu']:
                button.render(screen)

        elif self.state == 'playing':
            draw_gradient_background()
            self.snake.render(screen)
            self.food.render(screen)
            for particle in self.particles:
                particle.render(screen)
            
            # Draw scores
            font = pygame.font.Font(None, 36)
            score_text = f'Score: {self.snake.score}'
            high_score_text = f'Best: {self.high_score}'
            score_surface = font.render(score_text, True, SCORE_COLOR)
            high_score_surface = font.render(high_score_text, True, SCORE_COLOR)
            screen.blit(score_surface, (10, 10))
            screen.blit(high_score_surface, (WINDOW_SIZE - high_score_surface.get_width() - 10, 10))

            # Render snow particles
            for particle in self.snow_particles:
                particle.render(screen)

        elif self.state == 'game_over':
            screen.fill(MENU_BG_COLOR)
            if self.game_over_img:
                img_rect = self.game_over_img.get_rect(center=(WINDOW_SIZE//2, 150))
                screen.blit(self.game_over_img, img_rect)
            font = pygame.font.Font(None, 74)
            score_text = font.render(f"Score: {self.snake.score}", True, SCORE_COLOR)
            screen.blit(score_text, (WINDOW_SIZE//2 - score_text.get_width()//2, 300))
            for button in self.buttons['game_over']:
                button.render(screen)

def main():
    game = Game()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    for button_list in game.buttons.values():
                        for button in button_list:
                            if button.rect.collidepoint(mouse_pos):
                                # Stop any playing effect sounds before button action
                                if SOUND_ENABLED and game.effect_channel.get_busy():
                                    game.effect_channel.stop()
                                button.action()
            elif event.type == pygame.MOUSEMOTION:
                for button_list in game.buttons.values():
                    for button in button_list:
                        button.is_hovered = button.rect.collidepoint(mouse_pos)
            elif event.type == pygame.USEREVENT + 1:  # Background music volume restore
                if game.background_channel.get_busy():
                    game.background_channel.set_volume(0.5)
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Disable the timer

        game.update()
        game.render(screen)
        pygame.display.update()
        clock.tick(game.game_speed)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()