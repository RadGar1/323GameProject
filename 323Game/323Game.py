import math
import random
import pygame
import os

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
PLAYER_SPEED = 300

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)  # Color for walls

# Setup the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x, y))

class MusicPlayer(object):
    def __init__(self, music_file):
        pygame.mixer.init()
        self.music_file = music_file
        self.is_playing = False

    def play(self):
        if not self.is_playing:
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.is_playing = True

    def stop(self):
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, position, frames, animation_speed=0.1):
        super().__init__()
        self.frames = frames
        self.current_frame = 0
        self.animation_speed = animation_speed
        self.animation_time = 0
        self.image = frames[self.current_frame]
        self.rect = self.image.get_rect(center=position)
        self.pos = pygame.Vector2(position)
        self.direction = pygame.Vector2(0, 0)
        self.speed = PLAYER_SPEED
        
    def update(self, dt):
        # Animation update
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
        
        # Position update
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        
        # Store old position for collision handling
        old_pos = self.pos.copy()
        
        # Update position
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos
        
        # Keep sprite on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.pos.x, self.pos.y = self.rect.center
        
        return old_pos

class Player(AnimatedSprite):
    def __init__(self, x, y):
        # Sprite sheet dimensions
        self.sprite_width = 80
        self.sprite_height = 120
        self.cols = 2
        self.rows = 4
        
        # Load sprite sheet and create animation frames
        sprite_sheet = self.load_sprite_sheet("player.png", self.cols, self.rows)
        
        # Organize animations by direction
        self.animations = {
            "down": sprite_sheet[0:2],
            "left": sprite_sheet[2:4],
            "right": sprite_sheet[4:6],
            "up": sprite_sheet[6:8]
        }
        
        super().__init__((x, y), self.animations["down"])
        self.current_animation = "down"
        self.last_direction = "down"
        
    def load_sprite_sheet(self, filename, cols, rows):
        try:
            full_path = os.path.join("Sprites", filename)
            sprite_sheet = pygame.image.load(full_path).convert_alpha()
        except:
            # Fallback: create a placeholder sprite sheet
            print(f"Warning: Could not load {filename}, using placeholder")
            sprite_sheet = pygame.Surface((cols * self.sprite_width, rows * self.sprite_height), pygame.SRCALPHA)
            for row in range(rows):
                for col in range(cols):
                    x = col * self.sprite_width
                    y = row * self.sprite_height
                    color = (row * 60 % 255, 100 + col * 30 % 155, 50 + (row + col) * 20 % 205)
                    pygame.draw.rect(sprite_sheet, color, (x, y, self.sprite_width, self.sprite_height))
                    pygame.draw.rect(sprite_sheet, BLACK, (x, y, self.sprite_width, self.sprite_height), 1)
                    font = pygame.font.SysFont(None, 20)
                    direction = ["Down", "Left", "Right", "Up"][row]
                    text = font.render(f"{direction} {col+1}", True, BLACK)
                    sprite_sheet.blit(text, (x + 5, y + 5))
        
        frames = []
        for row in range(rows):
            for col in range(cols):
                frame = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
                frame.blit(sprite_sheet, (0, 0),
                          (col * self.sprite_width,
                           row * self.sprite_height,
                           self.sprite_width,
                           self.sprite_height))
                frames.append(frame)
        return frames
    
    def update(self, dt, walls):
        # Get keyboard input
        keys = pygame.key.get_pressed()
        move_vec = pygame.Vector2(0, 0)
        
        if keys[pygame.K_w]:
            move_vec.y -= 1
            self.last_direction = "up"
        if keys[pygame.K_s]:
            move_vec.y += 1
            self.last_direction = "down"
        if keys[pygame.K_a]:
            move_vec.x -= 1
            self.last_direction = "left"
        if keys[pygame.K_d]:
            move_vec.x += 1
            self.last_direction = "right"
            
        self.direction = move_vec
        
        # Change animation if direction changed
        if move_vec.length() > 0:
            if abs(move_vec.x) > abs(move_vec.y):
                self.current_animation = "left" if move_vec.x < 0 else "right"
            else:
                self.current_animation = "up" if move_vec.y < 0 else "down"
            
            # Update frames if animation changed
            if self.frames != self.animations[self.current_animation]:
                self.frames = self.animations[self.current_animation]
                self.current_frame = 0
        else:
            # When not moving, show first frame of last direction
            if self.frames != self.animations[self.last_direction]:
                self.frames = self.animations[self.last_direction]
                self.current_frame = 0
        
        # Call parent class update and get old position
        old_pos = super().update(dt)
        
        # Check for collisions with walls
        wall_collisions = pygame.sprite.spritecollide(self, walls, False)
        if wall_collisions:
            # Move back if colliding
            self.pos = old_pos
            self.rect.center = self.pos

class Mob(AnimatedSprite):
    def __init__(self, x, y):
        # Sprite sheet dimensions
        self.sprite_width = 64
        self.sprite_height = 64
        self.cols = 4
        self.rows = 1
        
        # Load sprite sheet and create animation frames
        sprite_sheet = self.load_sprite_sheet("Golem_Run.png", self.cols, self.rows)
        
        # Organize animations
        self.animations = {
            "right": sprite_sheet  # Just use all frames for simple animation
        }
        
        super().__init__((x, y), self.animations["right"])
        self.speed = 100  # Reduced speed for better collision handling
        
    def load_sprite_sheet(self, filename, cols, rows):
        try:
            full_path = os.path.join("Sprites", filename)
            sprite_sheet = pygame.image.load(full_path).convert_alpha()
        except:
            # Fallback: create a placeholder sprite sheet
            print(f"Warning: Could not load {filename}, using placeholder")
            sprite_sheet = pygame.Surface((cols * self.sprite_width, rows * self.sprite_height), pygame.SRCALPHA)
            for row in range(rows):
                for col in range(cols):
                    x = col * self.sprite_width
                    y = row * self.sprite_height
                    color = (row * 60 % 255, 100 + col * 30 % 155, 50 + (row + col) * 20 % 205)
                    pygame.draw.rect(sprite_sheet, color, (x, y, self.sprite_width, self.sprite_height))
                    pygame.draw.rect(sprite_sheet, (0, 0, 0), (x, y, self.sprite_width, self.sprite_height), 1)
        
        frames = []
        for row in range(rows):
            for col in range(cols):
                frame = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
                frame.blit(sprite_sheet, (0, 0),
                          (col * self.sprite_width,
                           row * self.sprite_height,
                           self.sprite_width,
                           self.sprite_height))
                frames.append(frame)
        return frames
    
    def update(self, dt, player, walls):
        # Get direction to player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            # Normalize direction
            dx /= dist
            dy /= dist
            self.direction = pygame.Vector2(dx, dy)
        
        # Call parent class update and get old position
        old_pos = super().update(dt)
        
        # Check for collisions with walls
        wall_collisions = pygame.sprite.spritecollide(self, walls, False)
        if wall_collisions:
            # Move back if colliding
            self.pos = old_pos
            self.rect.center = self.pos
        
        # If mob moves out of screen, reset position
        if self.rect.top > SCREEN_HEIGHT + 15 or self.rect.left < -15 or self.rect.right > SCREEN_WIDTH + 15:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.sprite_width)
            self.rect.y = random.randrange(-100, -50)

# Game setup
all_sprites = pygame.sprite.Group()
walls = pygame.sprite.Group()  # Group for walls

# Create some walls
wall_positions = [
    (100, 100, 200, 50),
    (400, 300, 50, 200),
    (700, 200, 200, 50),
    (900, 500, 300, 50)
]

for x, y, w, h in wall_positions:
    wall = Wall(x, y, w, h)
    all_sprites.add(wall)
    walls.add(wall)

player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
all_sprites.add(player)

music = MusicPlayer("2.Aria of the Soul(P4).mp3")
music.play()

mobs = pygame.sprite.Group()
for i in range(5):
    mob = Mob(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
    all_sprites.add(mob)
    mobs.add(mob)

# Game loop
running = True
dt = 0  # Delta time

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Update
    player.update(dt, walls)
    for mob in mobs:
        mob.update(dt, player, walls)
    
    # Check player-mob collisions
    collisions = pygame.sprite.spritecollide(player, mobs, False)
    if collisions:
        print("Player hit by mob!")
        running = False
    
    # Render
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # Flip display
    pygame.display.flip()
    
    # Cap FPS and get delta time
    dt = clock.tick(FPS) / 1000

pygame.quit()