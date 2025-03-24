import pygame
import random
import sys
import math
import os
import colorsys
import time
from pygame import gfxdraw

# Initialize Pygame
pygame.init()

# Initialize pygame mixer with specific settings
pygame.mixer.quit()  # Quit any existing mixer
pygame.mixer.init(44100, -16, 2, 2048)  # Increased buffer size for better sound handling
pygame.mixer.set_num_channels(8)  # Ensure we have enough channels

# Initialize global sound variables
SOUND_ENABLED = True
SOUNDS = {}

# Initialize sounds
def initialize_sounds():
    global SOUND_ENABLED, SOUNDS
    try:
        # Create assets directory if it doesn't exist
        if not os.path.exists("assets"):
            os.makedirs("assets")
            
        # Load sounds if they exist, otherwise create empty dictionary
        sound_files = {
            'eat': 'assets/eat.wav',
            'die': 'assets/die.wav',
            'menu': 'assets/menu.wav',
            'evolve': 'assets/evolve.wav',
            'portal': 'assets/portal.wav',
            'background': 'assets/background.wav',
            'poison': 'assets/poison.wav',
            'ice': 'assets/ice.wav',
            'start': 'assets/start.wav'
        }
        
        for sound_name, sound_path in sound_files.items():
            if os.path.exists(sound_path):
                SOUNDS[sound_name] = pygame.mixer.Sound(sound_path)
            else:
                print(f"Sound file {sound_path} not found")
                
        if not SOUNDS:
            print("No sound files found, disabling sound")
            SOUND_ENABLED = False
            
    except Exception as e:
        print(f"Error initializing sounds: {e}")
        SOUND_ENABLED = False

# Constants
WINDOW_SIZE = 720
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
MENU_BG_COLOR = (245, 245, 245)  # Light gray like Google
SCORE_COLOR = (95, 99, 104)  # Google grey
SNAKE_COLOR = (24, 128, 56)  # Google green
SNAKE_HEAD_COLOR = (21, 115, 50)  # Slightly darker green
FOOD_COLOR = (220, 53, 34)  # Google red
BUTTON_COLOR = (26, 115, 232)  # Google blue
BUTTON_HOVER_COLOR = (66, 133, 244)  # Lighter blue when hovering
BUTTON_TEXT_COLOR = (255, 255, 255)  # White text

# Screen dimensions
SCREEN_WIDTH = WINDOW_SIZE
SCREEN_HEIGHT = WINDOW_SIZE

# Frame rate
FPS = 10

# Fruits dictionary with colors and point values
FRUITS = {
    'apple': {'color': (255, 0, 0), 'points': 1},
    'orange': {'color': (255, 165, 0), 'points': 1},
    'banana': {'color': (255, 255, 0), 'points': 1},
    'berry': {'color': (138, 43, 226), 'points': 3},
    'kiwi': {'color': (75, 160, 0), 'points': 2},
    'ice_cream': {'color': (200, 200, 255), 'points': 2},
    'poison': {'color': (0, 255, 0), 'points': -2}
}

# Game settings with defaults
GAME_SETTINGS = {
    'reverse_controls': False,
    'ghost_mode': False,
    'maze_mode': False,
    'rainbow_snake': False,
    'big_food': False,
    'portal_mode': False,
    'wrap_around': True,
    'double_food': False,
    'infinite_length': False,
    'speed_increase': False
}

# Constants
GRID_COLOR = (240, 240, 240)  # Light grey for grid

# Add new constants
PARTICLE_COLORS = {
    'apple': [(255, 99, 71), (255, 69, 0)],
    'banana': [(255, 215, 0), (255, 193, 7)],
    'orange': [(255, 140, 0), (255, 152, 0)],
    'berry': [(186, 85, 211), (156, 39, 176)],
    'kiwi': [(139, 195, 74), (119, 175, 54)],
    'poison': [(58, 66, 71), (38, 46, 51)],
    'ice_cream': [(240, 248, 255), (230, 230, 250)]
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

def draw_gradient_background(surface):
    # Fill with white background
    surface.fill(WHITE)
    
    # Draw subtle grid lines
    for i in range(0, WINDOW_SIZE, GRID_SIZE):
        # Draw vertical lines
        pygame.draw.line(surface, GRID_COLOR, (i, 0), (i, WINDOW_SIZE))
        # Draw horizontal lines
        pygame.draw.line(surface, GRID_COLOR, (0, i), (WINDOW_SIZE, i))

def draw_rounded_rectangle(surface, color, rect, radius):
    x, y, width, height = rect
    pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, height))
    pygame.draw.rect(surface, color, (x, y + radius, width, height - 2*radius))
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius, y + height - radius), radius)

class Snake:
    def __init__(self, game):
        self.game = game  # Store the game reference
        self.length = 1
        self.positions = [((GRID_COUNT // 2), (GRID_COUNT // 2))]
        self.direction = (1, 0)  # Initially move right
        self.color = (24, 128, 56)  # Google green
        self.head_color = (21, 115, 50)  # Slightly darker green
        self.growth_pending = 0
        self.speed_multiplier = 1.0
        self.speed_effect_timer = 0
        self.speed_reduction_timer = 0
        self.rainbow_offset = 0
        self.evolution_stage = 0
        self.score = 0
        self.radius = GRID_SIZE // 2 - 1
        self.speed = 1  # Grid cells per update
        self.glow_factor = 0
        self.glow_increasing = True
        self.update_colors()  # This will set both color and head_color based on initial stage

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        # Handle rainbow snake setting
        if GAME_SETTINGS['rainbow_snake']:
            self.rainbow_offset = (self.rainbow_offset + 1) % 360
            h = (self.rainbow_offset / 360)
            r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
            self.color = (int(r * 255), int(g * 255), int(b * 255))
            self.head_color = (int(r * 200), int(g * 200), int(b * 200))  # Slightly darker head
        
        # Update speed reduction timer
        if self.speed_reduction_timer > 0:
            self.speed_reduction_timer -= 1
            if self.speed_reduction_timer == 0:
                self.speed = 1  # Restore normal speed

        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_COUNT, (cur[1] + y) % GRID_COUNT)
        
        # Handle wall collision if wrap around is disabled
        if not GAME_SETTINGS['wrap_around']:
            if new[0] < 0 or new[0] >= GRID_COUNT or new[1] < 0 or new[1] >= GRID_COUNT:
                return False
        
        # Check for collision with maze walls
        if hasattr(self.game, 'maze_walls') and new in self.game.maze_walls:
            return False
        
        # Check for self collision (unless ghost mode is enabled)
        if not GAME_SETTINGS['ghost_mode'] and new in self.positions[3:]:
            return False
            
        self.positions.insert(0, new)
        
        # Handle infinite length setting
        if GAME_SETTINGS['infinite_length']:
            if len(self.positions) > 3:  # Keep minimum length of 3
                self.positions.pop()
        else:
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

    def render(self, screen):
        # Draw snake body
        for i, pos in enumerate(self.positions):
            x = pos[0] * GRID_SIZE
            y = pos[1] * GRID_SIZE
            color = self.head_color if i == 0 else self.color

            # Draw snake segment with rounded corners if not the head
            if i == 0:
                # Head is a rounded rectangle
                draw_rounded_rectangle(screen, color, (x, y, GRID_SIZE, GRID_SIZE), 4)
            else:
                # Body segments are rounded rectangles
                draw_rounded_rectangle(screen, color, (x, y, GRID_SIZE, GRID_SIZE), 4)

            # Draw eyes only for head
            if i == 0:
                # Draw Google-style eyes (bigger white circles with smaller black pupils)
                eye_radius = 4
                pupil_radius = 2
                eye_offset = 7
                
                # Draw eyes based on direction
                if self.direction == (0, -1):  # Up
                    left_eye_pos = (x + eye_offset, y + eye_offset)
                    right_eye_pos = (x + GRID_SIZE - eye_offset, y + eye_offset)
                elif self.direction == (0, 1):  # Down
                    left_eye_pos = (x + eye_offset, y + GRID_SIZE - eye_offset)
                    right_eye_pos = (x + GRID_SIZE - eye_offset, y + GRID_SIZE - eye_offset)
                elif self.direction == (-1, 0):  # Left
                    left_eye_pos = (x + eye_offset, y + eye_offset)
                    right_eye_pos = (x + eye_offset, y + GRID_SIZE - eye_offset)
                else:  # Right (default)
                    left_eye_pos = (x + GRID_SIZE - eye_offset, y + eye_offset)
                    right_eye_pos = (x + GRID_SIZE - eye_offset, y + GRID_SIZE - eye_offset)
                
                # Draw the eyes
                pygame.draw.circle(screen, WHITE, left_eye_pos, eye_radius)
                pygame.draw.circle(screen, WHITE, right_eye_pos, eye_radius)
                
                # Draw pupils
                pygame.draw.circle(screen, BLACK, left_eye_pos, pupil_radius)
                pygame.draw.circle(screen, BLACK, right_eye_pos, pupil_radius)

            # Draw ghost effect if enabled
            if GAME_SETTINGS['ghost_mode'] and i > 0:
                ghost_surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                ghost_surface.fill((255, 255, 255, 128))  # Semi-transparent white
                screen.blit(ghost_surface, (x, y))

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
        self.radius = GRID_SIZE // 2 - 2
        self.randomize()

    def randomize(self):
        # Clear existing food
        self.positions = []
        
        # Add initial food
        self.add_food('apple')
        
        # Add second food if double food is enabled
        if GAME_SETTINGS['double_food']:
            self.add_food('apple')

    def add_food(self, fruit_type):
        # Find valid position not on snake or other food
        attempts = 0
        while attempts < 100:  # Limit attempts to prevent infinite loop
            # Generate random position
            new_pos = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
            
            # Check for collision with snake
            if new_pos in self.game.snake.positions:
                attempts += 1
                continue
                
            # Check for collision with other food
            if new_pos in [p[0] for p in self.positions]:
                attempts += 1
                continue
            
            # Valid position found
            break
        
        # If no valid position found after max attempts, don't add food
        if attempts >= 100:
            return
            
        # Determine fruit type
        if fruit_type == 'apple':
            # Select random fruit type
            fruit_types = ['apple', 'banana', 'orange', 'berry', 'kiwi']
            selected_type = random.choice(fruit_types)
            self.positions.append((new_pos, selected_type))

    def update(self):
        # Make sure we always have at least one food
        if not self.positions:
            self.add_food('apple')
            
        # Make sure we have two foods if double food is enabled
        if GAME_SETTINGS['double_food'] and len(self.positions) < 2:
            self.add_food('apple')

    def render(self, surface):
        for position, fruit_type in self.positions:
            x = position[0] * GRID_SIZE + GRID_SIZE // 2
            y = position[1] * GRID_SIZE + GRID_SIZE // 2
            
            # Get fruit color from FRUITS dictionary
            fruit_color = FRUITS.get(fruit_type, {'color': FOOD_COLOR})['color']
            
            if fruit_type == 'apple':
                # Improved apple with gradient and better shine
                darker_color = (max(0, fruit_color[0]-40), max(0, fruit_color[1]-40), max(0, fruit_color[2]-40))
                # Main apple body
                pygame.draw.circle(surface, fruit_color, (x, y), self.radius)
                # Bottom shadow
                pygame.draw.circle(surface, darker_color, (x, y+2), self.radius-1)
                # Top shine
                shine_pos = (x - self.radius//3, y - self.radius//3)
                pygame.draw.circle(surface, (255, 255, 255), shine_pos, 2)
                # Stem
                stem_start = (x, y - self.radius + 1)
                stem_end = (x + 2, y - self.radius - 3)
                pygame.draw.line(surface, (83, 40, 30), stem_start, stem_end, 2)
                # Leaf
                leaf_points = [(x + 2, y - self.radius - 2),
                              (x + 7, y - self.radius - 4),
                              (x + 4, y - self.radius)]
                pygame.draw.polygon(surface, (67, 160, 71), leaf_points)
                
            elif fruit_type == 'banana':
                # Improved banana with better curve and gradient
                lighter_color = (min(255, fruit_color[0]+40), min(255, fruit_color[1]+40), min(255, fruit_color[2]+40))
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
                # Highlight
                pygame.draw.line(surface, lighter_color, (x - 4, y - 2), (x + 4, y + 2), 2)
                
            elif fruit_type == 'orange':
                # Improved orange with segments
                pygame.draw.circle(surface, fruit_color, (x, y), self.radius)
                # Add texture/segments - ensure colors are valid
                segment_color = (max(0, min(255, fruit_color[0]-20)), 
                               max(0, min(255, fruit_color[1]-20)), 
                               max(0, min(255, fruit_color[2]-20)))
                for angle in range(0, 360, 60):
                    rad = math.radians(angle)
                    end_x = x + math.cos(rad) * (self.radius - 1)
                    end_y = y + math.sin(rad) * (self.radius - 1)
                    pygame.draw.line(surface, segment_color, (x, y), (end_x, end_y), 1)
                
            elif fruit_type == 'berry':
                # Draw berry as a cluster of small circles
                berry_size = self.radius - 2
                for dx, dy in [(0, 0), (-2, -2), (2, -2), (-2, 2), (2, 2)]:
                    pygame.draw.circle(surface, fruit_color, (x + dx, y + dy), berry_size)
                
            elif fruit_type == 'kiwi':
                # Kiwi as a green circle with seeds
                pygame.draw.circle(surface, fruit_color, (x, y), self.radius)
                # Add seeds
                for _ in range(8):
                    seed_x = x + random.randint(-self.radius//2, self.radius//2)
                    seed_y = y + random.randint(-self.radius//2, self.radius//2)
                    pygame.draw.circle(surface, (0, 0, 0), (seed_x, seed_y), 1)
                    
            elif fruit_type == 'ice_cream':
                # Draw ice cream cone
                cone_color = (210, 180, 140)  # Tan color for cone
                ice_color = (240, 248, 255)   # White for ice cream
                
                # Draw cone
                cone_points = [
                    (x, y + self.radius),
                    (x - self.radius, y - self.radius//2),
                    (x + self.radius, y - self.radius//2)
                ]
                pygame.draw.polygon(surface, cone_color, cone_points)
                
                # Draw ice cream scoop
                pygame.draw.circle(surface, ice_color, (x, y - self.radius//2), self.radius)
                
            elif fruit_type == 'poison':
                # Draw poison as a skull
                pygame.draw.circle(surface, fruit_color, (x, y), self.radius)
                # Draw skull eyes
                eye_size = self.radius // 3
                pygame.draw.circle(surface, (255, 255, 255), (x - eye_size, y - eye_size), eye_size)
                pygame.draw.circle(surface, (255, 255, 255), (x + eye_size, y - eye_size), eye_size)
                # Draw skull mouth
                pygame.draw.rect(surface, (255, 255, 255), (x - eye_size, y + eye_size - 1, eye_size*2, eye_size))
                # Draw teeth
                pygame.draw.line(surface, fruit_color, (x - eye_size//2, y + eye_size - 1), 
                               (x - eye_size//2, y + eye_size*2 - 1), 1)
                pygame.draw.line(surface, fruit_color, (x + eye_size//2, y + eye_size - 1), 
                               (x + eye_size//2, y + eye_size*2 - 1), 1)
            else:
                # Default circular food
                pygame.draw.circle(surface, fruit_color, (x, y), self.radius)

class Particle:
    def __init__(self, x, y, color=(255, 255, 255), velocity=None, lifetime=30, size=3):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.original_lifetime = lifetime
        self.size = size
        
        # Initialize random velocity if not provided
        if velocity is None:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
        else:
            self.velocity = velocity
            
    def update(self):
        # Move the particle
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        
        # Decrease lifetime
        self.lifetime -= 1
        
        # Optionally adjust size based on lifetime
        self.size = max(1, self.size * (self.lifetime / self.original_lifetime))
        
    def render(self, surface):
        # Adjust transparency based on lifetime
        alpha = int(255 * (self.lifetime / self.original_lifetime))
        
        # Draw the particle
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

class SnowParticle:
    def __init__(self, x, y, speed=1):
        self.x = x
        self.y = y
        self.speed = speed
        self.lifetime = random.randint(100, 300)
        self.original_lifetime = self.lifetime
        self.size = random.randint(1, 3)
        self.color = (255, 255, 255)
        
    def update(self):
        # Move downward with slight side-to-side drift
        self.y += self.speed
        self.x += random.uniform(-0.5, 0.5)
        
        # Decrease lifetime
        self.lifetime -= 1
        
    def render(self, surface):
        # Adjust transparency based on lifetime
        alpha = int(255 * (self.lifetime / self.original_lifetime))
        
        # Draw the snow particle
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

class Button:
    def __init__(self, x, y, width, height, text, action, color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False
        self.color = color
        self.hover_color = hover_color
        
    def render(self, surface):
        # Draw button background with rounded corners
        current_color = self.hover_color if self.is_hovered else self.color
        draw_rounded_rectangle(surface, current_color, self.rect, 8)
        
        # Draw button text
        font = pygame.font.Font(None, 28)
        text_surface = font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        # Add a slight shadow effect for non-hovered buttons
        if not self.is_hovered:
            shadow_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height, self.rect.width, 2)
            shadow_color = (80, 80, 80)  # Dark gray shadow
            draw_rounded_rectangle(surface, shadow_color, shadow_rect, 2)
        
    def update_scroll_position(self, scroll_offset):
        self.rect.y = self.original_y - scroll_offset

class Portal:
    def __init__(self, start_pos, end_pos):
        self.start_pos = start_pos  # (x, y) in grid coordinates
        self.end_pos = end_pos      # (x, y) in grid coordinates
        self.radius = GRID_SIZE // 2
        self.lifetime = 200         # Duration in frames
        self.start_color = (0, 191, 255)  # Deep sky blue
        self.end_color = (138, 43, 226)   # Blue violet
        self.color = self.start_color  # For backward compatibility
        self.particles = []
        self.particle_timer = 0
        
        # Create initial particles for both portals
        self.create_particles(self.start_pos, self.start_color, 20)
        self.create_particles(self.end_pos, self.end_color, 20)
    
    def create_particles(self, position, color, count):
        x = position[0] * GRID_SIZE + GRID_SIZE // 2
        y = position[1] * GRID_SIZE + GRID_SIZE // 2
        
        for _ in range(count):
            # Create particles in a circular pattern
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.radius)
            px = x + math.cos(angle) * distance
            py = y + math.sin(angle) * distance
            
            # Random velocity toward center
            vx = (x - px) * random.uniform(0.01, 0.03)
            vy = (y - py) * random.uniform(0.01, 0.03)
            
            particle = PortalParticle(px, py, color, (vx, vy))
            self.particles.append(particle)
    
    def update(self):
        # Update lifetime
        self.lifetime -= 1
        
        # Generate new particles periodically
        self.particle_timer += 1
        if self.particle_timer >= 5:  # Every 5 frames
            self.particle_timer = 0
            self.create_particles(self.start_pos, self.start_color, 2)
            self.create_particles(self.end_pos, self.end_color, 2)
        
        # Update existing particles
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
    
    def render(self, surface):
        # Draw portals
        start_x = self.start_pos[0] * GRID_SIZE + GRID_SIZE // 2
        start_y = self.start_pos[1] * GRID_SIZE + GRID_SIZE // 2
        end_x = self.end_pos[0] * GRID_SIZE + GRID_SIZE // 2
        end_y = self.end_pos[1] * GRID_SIZE + GRID_SIZE // 2
        
        # Draw portal rings with pulsating effect
        pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.2 + 0.8
        
        # Ensure color values are valid integers
        start_pulse_color = tuple(max(0, min(255, int(c * pulse))) for c in self.start_color)
        end_pulse_color = tuple(max(0, min(255, int(c * pulse))) for c in self.end_color)
        
        pygame.draw.circle(surface, start_pulse_color, (start_x, start_y), self.radius)
        pygame.draw.circle(surface, end_pulse_color, (end_x, end_y), self.radius)
        
        # Draw portal centers
        pygame.draw.circle(surface, (255, 255, 255), (start_x, start_y), self.radius // 3)
        pygame.draw.circle(surface, (255, 255, 255), (end_x, end_y), self.radius // 3)
        
        # Draw particles
        for particle in self.particles:
            particle.render(surface)

class PortalParticle:
    def __init__(self, x, y, color, velocity):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.lifetime = 20
        self.size = random.uniform(1, 3)
    
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.lifetime -= 1
        self.size = max(0, self.size - 0.1)
    
    def render(self, surface):
        alpha = int(255 * (self.lifetime / 20))
        particle_surface = pygame.Surface((int(self.size * 2 + 1), int(self.size * 2 + 1)), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (*self.color, alpha), (int(self.size + 1), int(self.size + 1)), int(self.size))
        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))

class Game:
    def __init__(self):
        global SOUND_ENABLED
        self.snake = Snake(self)
        self.food = Food(self)
        self.particles = []
        self.snow_particles = []
        self.portals = []
        self.maze_walls = set()
        self.high_score = 0
        self.game_over = False
        self.menu_state = 'menu'  # 'menu', 'settings', 'playing', 'game_over'
        self.current_menu = 'menu'  # 'menu', 'settings'
        self.buttons = []
        self.settings_buttons = []
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Game speed settings
        self.current_speed_index = 1  # 0=Slow, 1=Normal, 2=Fast
        self.speed_levels = [5, 10, 15]  # FPS values for different speeds
        
        # Load game over image if available
        try:
            self.game_over_img = pygame.image.load('assets/game_over.png')
            self.game_over_img = pygame.transform.scale(self.game_over_img, (300, 300))
        except:
            self.game_over_img = None

        # Setup menu buttons
        self.setup_menu()

        # Sound setup
        self.sound_channels = {}
        if SOUND_ENABLED:
            self.initialize_sound_channels()

    def initialize_sound_channels(self):
        # Initialize sound channels
        self.sound_channels['background'] = pygame.mixer.Channel(0)
        self.sound_channels['effect'] = pygame.mixer.Channel(1)
        self.sound_channels['evolution'] = pygame.mixer.Channel(2)
        
        # Set background music to loop
        if 'background' in SOUNDS:
            self.sound_channels['background'].play(SOUNDS['background'], loops=-1)
            self.sound_channels['background'].set_volume(0.5)

    def play_sound(self, sound_name):
        if SOUND_ENABLED and sound_name in SOUNDS:
            if sound_name == 'background':
                self.sound_channels['background'].play(SOUNDS[sound_name], loops=-1)
                self.sound_channels['background'].set_volume(0.5)
            else:
                self.sound_channels['effect'].play(SOUNDS[sound_name])

    def start_game(self):
        self.snake = Snake(self)
        self.food = Food(self)
        self.particles = []
        self.snow_particles = []
        self.portals = []
        self.maze_walls = set()
        self.game_over = False
        self.menu_state = 'playing'
        
        # Initialize maze if maze mode is enabled
        if GAME_SETTINGS['maze_mode']:
            self.generate_maze()
            self.maze_update_timer = FPS * 15  # Regenerate maze every 15 seconds
            
        # Initialize portals if portal mode is enabled
        if GAME_SETTINGS['portal_mode']:
            self.generate_portals()

        # Play game start sound
        self.play_sound('start')

    def show_settings(self):
        # Change game state to settings
        self.menu_state = 'settings'
        self.current_menu = 'settings'
        
        # Play sound if enabled
        self.play_sound('menu')
        
        print("Settings menu opened")

    def toggle_setting(self, setting):
        # Toggle the setting value
        GAME_SETTINGS[setting] = not GAME_SETTINGS[setting]
        
        # Format the setting name for display
        display_name = ' '.join(setting.split('_')).title()
        
        # Find and update the button text for this setting
        for button in self.settings_buttons:
            if button.text.startswith(display_name):
                state = "On" if GAME_SETTINGS[setting] else "Off"
                button.text = f"{display_name}: {state}"
                print(f"Setting '{setting}' changed to {GAME_SETTINGS[setting]}")
                break
                
        # Play sound if enabled
        self.play_sound('menu')

    def cycle_speed(self):
        # Cycle through speed levels
        self.current_speed_index = (self.current_speed_index + 1) % len(self.speed_levels)
        
        # Update button text
        speed_names = ['Slow', 'Normal', 'Fast']
        for button in self.buttons:
            if button.text.startswith("Speed:"):
                button.text = f"Speed: {speed_names[self.current_speed_index]}"
                break
                
        # Play sound if enabled
        self.play_sound('menu')

    def setup_menu(self):
        # Button dimensions and positioning
        button_width = 250
        button_height = 50
        button_spacing = 50
        center_x = WINDOW_SIZE // 2
        start_y = 200
        
        # Main menu buttons
        self.buttons = [
            Button(center_x - button_width // 2, start_y, button_width, button_height,
                  "Start Game", lambda: self.start_game()),
            Button(center_x - button_width // 2, start_y + button_spacing, button_width, button_height,
                  "Settings", lambda: self.show_settings()),
            Button(center_x - button_width // 2, start_y + button_spacing * 2, button_width, button_height,
                  f"Speed: {['Slow', 'Normal', 'Fast'][self.current_speed_index]}", lambda: self.cycle_speed())
        ]

        # Settings buttons in a vertical list
        settings_start_y = 130
        self.settings_buttons = []
        
        # List of settings to display
        settings_to_display = [
            'reverse_controls',
            'ghost_mode',
            'maze_mode',
            'rainbow_snake',
            'big_food',
            'portal_mode',
            'wrap_around',
            'double_food',
            'infinite_length',
            'speed_increase'
        ]
        
        # Create a button for each setting
        for i, setting in enumerate(settings_to_display):
            # Format the setting name for display
            display_name = ' '.join(setting.split('_')).title()
            
            # Determine if setting is enabled
            state = "On" if GAME_SETTINGS[setting] else "Off"
            
            # Create button with toggle function
            button = Button(
                center_x - button_width // 2,
                settings_start_y + i * button_spacing,
                button_width,
                button_height,
                f"{display_name}: {state}",
                lambda s=setting: self.toggle_setting(s),
                color=(50, 50, 50),
                hover_color=(80, 80, 80)
            )
            self.settings_buttons.append(button)

        # Add back button to settings at the bottom
        self.settings_buttons.append(
            Button(
                center_x - button_width // 2,
                settings_start_y + len(settings_to_display) * button_spacing,
                button_width,
                button_height,
                "Back to Menu",
                lambda: self.show_menu(),
                color=(70, 70, 100),
                hover_color=(90, 90, 120)
            )
        )

    def set_speed(self, multiplier):
        self.speed_multiplier = multiplier
        self.game_speed = int(self.base_speed * multiplier)

    def show_menu(self):
        # Change game state to menu
        self.menu_state = 'menu'
        
        # Update speed button text
        speed_names = ['Slow', 'Normal', 'Fast']
        for button in self.buttons:
            if button.text.startswith("Speed:"):
                button.text = f"Speed: {speed_names[self.current_speed_index]}"
        
        # Play sound if enabled
        if SOUND_ENABLED:
            # Stop all sounds first
            self.sound_channels['background'].stop()
            self.sound_channels['effect'].stop()
            self.sound_channels['evolution'].stop()
            # Play menu sound if available
            if 'menu' in SOUNDS:
                self.sound_channels['effect'].play(SOUNDS['menu'])
        
        print("Main menu opened")

    def update(self):
        # In menu state, no game update needed
        if self.menu_state != 'playing':
            return

        # Handle reverse controls
        key_mapping = {
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0)
        }
        
        if GAME_SETTINGS['reverse_controls']:
            key_mapping = {
                pygame.K_UP: (0, 1),     # Up key moves down
                pygame.K_DOWN: (0, -1),  # Down key moves up
                pygame.K_LEFT: (1, 0),   # Left key moves right
                pygame.K_RIGHT: (-1, 0)  # Right key moves left
            }
            
        # Update the snake
        if not self.snake.update():
            self.game_over = True
            self.play_sound('death')
            return
            
        # Check for collisions (both with portals and food)
        self.check_collisions()
            
        # Update particles
        self.update_particles()
            
        # Handle maze regeneration
        if GAME_SETTINGS['maze_mode']:
            if hasattr(self, 'maze_update_timer'):
                self.maze_update_timer -= 1
                if self.maze_update_timer <= 0:
                    self.regenerate_maze()
                    self.maze_update_timer = FPS * 15  # Regenerate maze every 15 seconds

    def create_particles(self, position=None, count=10, color=None):
        # If position not specified, use snake head position
        if position is None:
            position = self.snake.get_head_position()
            
        x = position[0] * GRID_SIZE + GRID_SIZE // 2
        y = position[1] * GRID_SIZE + GRID_SIZE // 2
        
        # If color not specified, use food color based on recently eaten food
        if color is None:
            for i, (food_pos, food_type) in enumerate(self.food.positions):
                if position == food_pos:
                    if food_type in PARTICLE_COLORS:
                        color = random.choice(PARTICLE_COLORS[food_type])
                    else:
                        color = FOOD_COLOR
                    break
            else:
                # Default to food color if no match found
                color = FOOD_COLOR
        
        # Ensure count is an integer
        if not isinstance(count, int):
            count = 10  # Default to 10 particles
        
        # Create particles
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

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
        if self.menu_state == 'menu':
            screen.fill(MENU_BG_COLOR)
            font = pygame.font.Font(None, 74)
            title = font.render("Snake Game", True, SCORE_COLOR)
            screen.blit(title, (WINDOW_SIZE//2 - title.get_width()//2, 100))
            for button in self.buttons:
                button.render(screen)
        elif self.menu_state == 'settings':
            screen.fill(MENU_BG_COLOR)
            font = pygame.font.Font(None, 74)
            title = font.render("Settings", True, SCORE_COLOR)
            screen.blit(title, (WINDOW_SIZE//2 - title.get_width()//2, 50))
            for button in self.settings_buttons:
                button.render(screen)
        elif self.menu_state == 'playing':
            # Draw background
            draw_gradient_background(screen)
            
            # Draw maze walls if enabled
            if GAME_SETTINGS['maze_mode'] and self.maze_walls:
                for wall in self.maze_walls:
                    x = wall[0] * GRID_SIZE
                    y = wall[1] * GRID_SIZE
                    pygame.draw.rect(screen, GRAY, (x, y, GRID_SIZE, GRID_SIZE))
            
            # Draw portals if enabled
            if GAME_SETTINGS['portal_mode']:
                for portal in self.portals:
                    portal.render(screen)
            
            # Draw the food
            self.food.render(screen)
            
            # Draw the snake
            self.snake.render(screen)
            
            # Draw particles
            for particle in self.particles:
                particle.render(screen)
                
            # Draw snow particles
            for particle in self.snow_particles:
                particle.render(screen)
            
            # Draw score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {self.snake.score}", True, SCORE_COLOR)
            high_score_text = font.render(f"High Score: {self.high_score}", True, SCORE_COLOR)
            screen.blit(score_text, (10, 10))
            screen.blit(high_score_text, (10, 50))
            
            # Draw game over screen if game is over
            if self.game_over:
                # Semi-transparent overlay
                overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                screen.blit(overlay, (0, 0))
                
                # Game over text
                font = pygame.font.Font(None, 74)
                game_over_text = font.render("Game Over", True, WHITE)
                screen.blit(game_over_text, (WINDOW_SIZE//2 - game_over_text.get_width()//2, 200))
                
                # Score text
                font = pygame.font.Font(None, 48)
                final_score = font.render(f"Score: {self.snake.score}", True, WHITE)
                screen.blit(final_score, (WINDOW_SIZE//2 - final_score.get_width()//2, 300))
                
                # Restart instructions
                font = pygame.font.Font(None, 36)
                restart_text = font.render("Press ESC to return to menu", True, WHITE)
                screen.blit(restart_text, (WINDOW_SIZE//2 - restart_text.get_width()//2, 400))
                
        elif self.menu_state == 'game_over':
            screen.fill(MENU_BG_COLOR)
            if self.game_over_img:
                screen.blit(self.game_over_img, (WINDOW_SIZE//2 - 150, 150))
                
            font = pygame.font.Font(None, 74)
            game_over_text = font.render("Game Over", True, SCORE_COLOR)
            screen.blit(game_over_text, (WINDOW_SIZE//2 - game_over_text.get_width()//2, 100))
            
            font = pygame.font.Font(None, 48)
            score_text = font.render(f"Score: {self.snake.score}", True, SCORE_COLOR)
            screen.blit(score_text, (WINDOW_SIZE//2 - score_text.get_width()//2, 300))
            for button in self.buttons:
                button.render(screen)

    def generate_maze(self):
        self.maze_walls = set()
        if not GAME_SETTINGS['maze_mode']:
            return
        
        # Clear existing maze
        self.maze_walls = set()
        
        # Generate random maze obstacles
        obstacle_count = int(GRID_COUNT * GRID_COUNT * 0.05)  # 5% of grid cells
        snake_positions = set(self.snake.positions)
        food_positions = set(pos for pos, _ in self.food.positions)
        forbidden_positions = snake_positions.union(food_positions)
        
        # Add buffer around snake head to prevent immediate collisions
        head_pos = self.snake.get_head_position()
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                buffer_pos = ((head_pos[0] + dx) % GRID_COUNT, 
                             (head_pos[1] + dy) % GRID_COUNT)
                forbidden_positions.add(buffer_pos)
        
        # Generate wall positions
        for _ in range(obstacle_count):
            # Find valid wall position
            for _ in range(100):  # Limit attempts to find valid position
                wall_pos = (random.randint(0, GRID_COUNT-1), 
                           random.randint(0, GRID_COUNT-1))
                if wall_pos not in forbidden_positions and wall_pos not in self.maze_walls:
                    self.maze_walls.add(wall_pos)
                    forbidden_positions.add(wall_pos)
                    break
        
        # Add some connected walls to make it more maze-like
        for _ in range(obstacle_count // 2):
            if not self.maze_walls:
                break
                
            # Pick a random existing wall
            wall = random.choice(tuple(self.maze_walls))
            
            # Try to extend it in a random direction
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                new_wall = ((wall[0] + dx) % GRID_COUNT, 
                           (wall[1] + dy) % GRID_COUNT)
                if new_wall not in forbidden_positions and new_wall not in self.maze_walls:
                    self.maze_walls.add(new_wall)
                    forbidden_positions.add(new_wall)
                    break
    
    def render_maze(self, surface):
        if not GAME_SETTINGS['maze_mode'] or not self.maze_walls:
            return
            
        for wall_pos in self.maze_walls:
            x = wall_pos[0] * GRID_SIZE
            y = wall_pos[1] * GRID_SIZE
            
            # Draw wall with texture
            wall_color = (100, 100, 100)  # Dark gray
            pygame.draw.rect(surface, wall_color, (x, y, GRID_SIZE, GRID_SIZE))
            
            # Add brick pattern
            highlight_color = (120, 120, 120)  # Slightly lighter gray
            shadow_color = (80, 80, 80)  # Slightly darker gray
            
            # Horizontal lines
            for i in range(2):
                line_y = y + (i+1) * GRID_SIZE // 3
                pygame.draw.line(surface, shadow_color, (x, line_y), (x + GRID_SIZE, line_y))
                pygame.draw.line(surface, highlight_color, (x, line_y + 1), (x + GRID_SIZE, line_y + 1))
            
            # Vertical lines - offset every other row to create a brick pattern
            offset = (wall_pos[1] % 2) * (GRID_SIZE // 2)
            for i in range(1):
                line_x = x + offset + i * GRID_SIZE
                if line_x < x + GRID_SIZE:
                    pygame.draw.line(surface, shadow_color, (line_x, y), (line_x, y + GRID_SIZE))
                    pygame.draw.line(surface, highlight_color, (line_x + 1, y), (line_x + 1, y + GRID_SIZE))

    def update_portals(self):
        # Only handle portals if portal mode is enabled
        if not GAME_SETTINGS['portal_mode']:
            self.portals = []  # Clear portals if mode is disabled
            return
            
        # Update existing portals
        for portal in self.portals:
            portal.update()
            if portal.lifetime <= 0:
                self.portals.remove(portal)
        
        # Spawn new portals periodically
        self.portal_spawn_timer += 1
        if self.portal_spawn_timer >= self.portal_spawn_interval and len(self.portals) < 2:
            self.portal_spawn_timer = 0
            self.create_portal()
        
        # Check if snake head is entering a portal
        if self.portals:
            self.check_portal_collision()
    
    def create_portal(self):
        # Find valid positions for portal entrance and exit
        available_positions = []
        
        # Positions that are not valid for portals
        forbidden_positions = set(self.snake.positions)
        for food_pos, _ in self.food.positions:
            forbidden_positions.add(food_pos)
        for portal in self.portals:
            forbidden_positions.add(portal.start_pos)
            forbidden_positions.add(portal.end_pos)
        for wall_pos in self.maze_walls:
            forbidden_positions.add(wall_pos)
        
        # Collect all valid positions
        for x in range(GRID_COUNT):
            for y in range(GRID_COUNT):
                if (x, y) not in forbidden_positions:
                    available_positions.append((x, y))
        
        # Ensure we have at least 2 positions available
        if len(available_positions) < 2:
            return
        
        # Pick two random positions for the portal
        start_pos, end_pos = random.sample(available_positions, 2)
        
        # Create the portal
        self.portals.append(Portal(start_pos, end_pos))
        
        # Play portal sound if available
        if SOUND_ENABLED and 'portal' in SOUNDS:
            self.sound_channels['effect'].play(SOUNDS['portal'])
    
    def check_portal_collision(self):
        head_pos = self.snake.get_head_position()
        
        for portal in self.portals:
            # Check if snake head is at portal entrance
            if head_pos == portal.start_pos:
                # Teleport to exit
                self.snake.positions[0] = portal.end_pos
                # Create particles at both entrance and exit
                self.create_particles(portal.start_pos, portal.start_color, 15)
                self.create_particles(portal.end_pos, portal.end_color, 15)
                # Play portal sound if available
                if SOUND_ENABLED and 'portal' in SOUNDS:
                    self.sound_channels['effect'].play(SOUNDS['portal'])
                break
            # Check if snake head is at portal exit
            elif head_pos == portal.end_pos:
                # Teleport to entrance
                self.snake.positions[0] = portal.start_pos
                # Create particles at both entrance and exit
                self.create_particles(portal.end_pos, portal.end_color, 15)
                self.create_particles(portal.start_pos, portal.start_color, 15)
                # Play portal sound if available
                if SOUND_ENABLED and 'portal' in SOUNDS:
                    self.sound_channels['effect'].play(SOUNDS['portal'])
                break

    def check_collisions(self):
        # Check portal collisions
        if self.portals and GAME_SETTINGS['portal_mode']:
            head_pos = self.snake.get_head_position()
            for portal in self.portals:
                if head_pos == portal.start_pos:
                    # Create particles at portal location
                    self.create_particles(portal.start_pos, 15, portal.color)
                    
                    # Get new position after teleportation
                    new_pos = portal.end_pos
                    
                    # Update snake head position
                    self.snake.positions[0] = new_pos
                    self.play_sound('portal')
                    return True
        
        # Check food collisions
        head_pos = self.snake.get_head_position()
        to_remove = []
        
        for i, (position, fruit_type) in enumerate(self.food.positions):
            if head_pos == position:
                # Mark this food item for removal
                to_remove.append(i)
                
                # Handle different fruit types
                if fruit_type != 'poison':
                    # Create particles based on fruit color
                    fruit_color = FRUITS.get(fruit_type, {'color': FOOD_COLOR})['color']
                    self.create_particles(position, 10, fruit_color)
                    
                    # Apple, orange, banana - normal growth
                    if fruit_type in ['apple', 'orange', 'banana']:
                        self.snake.growth_pending += 1
                        self.snake.score += 1
                    # Berry - extra growth
                    elif fruit_type == 'berry':
                        self.snake.growth_pending += 2
                        self.snake.score += 3
                    # Kiwi - speed increase
                    elif fruit_type == 'kiwi':
                        self.snake.speed_multiplier = 2.0
                        self.snake.speed_effect_timer = FPS * 5  # 5 seconds
                        self.snake.score += 2
                    # Ice cream - snow effect
                    elif fruit_type == 'ice_cream':
                        # Add snow particles
                        for _ in range(50):
                            x = random.randint(0, SCREEN_WIDTH)
                            y = random.randint(-50, 0)
                            speed = random.uniform(1, 3)
                            self.snow_particles.append(SnowParticle(x, y, speed))
                        self.snake.score += 2
                    
                    self.play_sound('eat')
                else:
                    # Poison - negative effect
                    self.snake.speed_reduction_timer = FPS * 3  # 3 seconds of reduced speed
                    self.snake.score = max(0, self.snake.score - 2)  # Reduce score, minimum 0
                    self.play_sound('poison')
        
        # Remove eaten food items
        if to_remove:
            # Remove in reverse order to avoid index shifts
            for i in sorted(to_remove, reverse=True):
                del self.food.positions[i]
            
            # Spawn new food
            self.food.update()
            
        return False

    def update_particles(self):
        # Update regular particles
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
                
        # Update snow particles
        for particle in self.snow_particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.snow_particles.remove(particle)
                
        # Generate more snow particles if ice cream effect is active
        if hasattr(self, 'ice_cream_active') and self.ice_cream_active:
            # Add occasional snow particles from the top of the screen
            if random.random() < 0.2:  # 20% chance each frame
                x = random.randint(0, WINDOW_SIZE)
                y = -5
                speed = random.uniform(1, 3)
                self.snow_particles.append(SnowParticle(x, y, speed))

    def generate_portals(self):
        # Only create portals if portal mode is enabled
        if not GAME_SETTINGS['portal_mode']:
            return
            
        # Clear existing portals
        self.portals = []
        
        # Create a new portal
        self.create_portal()

def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_SIZE
    
    # Initialize pygame and create window
    pygame.init()
    pygame.mixer.init()
    
    # Initialize sounds
    initialize_sounds()
    
    # Create game screen
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption('Snake Evolution')
    
    # Create clock for controlling game speed
    clock = pygame.time.Clock()
    
    # Create game instance
    game = Game()
    
    # Main game loop
    while True:
        # Process events
        for event in pygame.event.get():
            # Check for quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Handle mouse clicks for menu navigation
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    # Get the current state's buttons
                    current_buttons = game.buttons if game.menu_state == 'menu' else game.settings_buttons
                    for button in current_buttons:
                        if button.rect.collidepoint(mouse_pos):
                            # Call the button action
                            button.action()
                            print(f"Button clicked: {button.text}")
            
            # Update button hover state on mouse movement
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                current_buttons = game.buttons if game.menu_state == 'menu' else game.settings_buttons
                for button in current_buttons:
                    button.is_hovered = button.rect.collidepoint(mouse_pos)
                            
            # Handle key presses for snake movement
            if event.type == pygame.KEYDOWN and game.menu_state == 'playing':
                # Handle control keys based on reverse_controls setting
                direction = game.snake.direction
                
                # Normal controls
                if not GAME_SETTINGS['reverse_controls']:
                    if event.key == pygame.K_UP and direction != (0, 1):
                        game.snake.direction = (0, -1)
                    elif event.key == pygame.K_DOWN and direction != (0, -1):
                        game.snake.direction = (0, 1)
                    elif event.key == pygame.K_LEFT and direction != (1, 0):
                        game.snake.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                        game.snake.direction = (1, 0)
                # Reverse controls
                else:
                    if event.key == pygame.K_UP and direction != (0, -1):
                        game.snake.direction = (0, 1)  # Up key moves down
                    elif event.key == pygame.K_DOWN and direction != (0, 1):
                        game.snake.direction = (0, -1)  # Down key moves up
                    elif event.key == pygame.K_LEFT and direction != (-1, 0):
                        game.snake.direction = (1, 0)  # Left key moves right
                    elif event.key == pygame.K_RIGHT and direction != (1, 0):
                        game.snake.direction = (-1, 0)  # Right key moves left
                
                # Escape key to return to menu
                if event.key == pygame.K_ESCAPE:
                    game.show_menu()
                        
        # Update game state
        game.update()
        
        # Clear the screen
        screen.fill(BLACK)
        
        # Render the game
        game.render(screen)
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(FPS)

if __name__ == '__main__':
    main()