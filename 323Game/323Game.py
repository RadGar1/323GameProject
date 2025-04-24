import math
import random
import pygame
import os
import pytmx

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
PLAYER_SPEED = 300

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Setup the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Lone Voyager")
clock = pygame.time.Clock()

def draw_text(surface, text, size, color, x, y, center=True):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(topleft=(x, y))
    surface.blit(text_surface, text_rect)

def draw_map(surface, tmx_data):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    surface.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

def show_start_screen():
    screen.fill(BLACK)
    draw_text(screen, "LONE VOYAGER", 64, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    draw_text(screen, "WASD or Arrow Keys to Move", 36, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text(screen, "P: Stun | O: Interact | I: Cipher Wheel", 36, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
    draw_text(screen, "Press any key to begin", 36, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3/4)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYUP:
                waiting = False
    return True

def show_game_over_screen():
    screen.fill(BLACK)
    draw_text(screen, "GAME OVER", 64, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    draw_text(screen, "Press any key to play again", 36, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYUP:
                waiting = False
    return True

def show_message_screen(message):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    message_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3, 
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
    pygame.draw.rect(screen, WHITE, message_rect)
    pygame.draw.rect(screen, BLACK, message_rect, 2)
    
    font = pygame.font.Font(None, 36)
    words = message.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] < message_rect.width - 40:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    
    y_offset = message_rect.y + 20
    for line in lines:
        draw_text(screen, line, 36, BLACK, SCREEN_WIDTH // 2, y_offset)
        y_offset += 40
    
    draw_text(screen, "Press ENTER to continue", 36, BLACK, SCREEN_WIDTH // 2, message_rect.bottom - 40)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False
    return True

class WheelCipher:
    def __init__(self):
        self.radius = 200
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        self.outer_angle = 0
        self.visible = False
        self.rotation_speed = 2
        self.outer_letters = "ABCDEFGHIJKLMNO"
        self.inner_numbers = [str(i) for i in range(1, 16)]
        
    def draw(self, surface, suspicion_level):
        if not self.visible:
            return
            
        # Draw semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Draw outer circle (letters)
        pygame.draw.circle(surface, WHITE, (self.center_x, self.center_y), self.radius, 2)
        
        # Draw inner circle (numbers)
        pygame.draw.circle(surface, WHITE, (self.center_x, self.center_y), self.radius // 2, 2)
        
        # Draw outer letters
        for i, letter in enumerate(self.outer_letters):
            angle = math.radians(self.outer_angle + i * (360 / len(self.outer_letters)))
            x = self.center_x + (self.radius - 20) * math.cos(angle)
            y = self.center_y + (self.radius - 20) * math.sin(angle)
            draw_text(surface, letter, 30, WHITE, x, y)
            
            # Draw red indicator at K when suspicion is high
            if suspicion_level > 80 and letter == "K":
                pygame.draw.line(surface, RED, 
                               (self.center_x, self.center_y),
                               (x, y), 2)
        
        # Draw inner numbers
        for i, number in enumerate(self.inner_numbers):
            angle = math.radians(i * (360 / len(self.inner_numbers)))
            x = self.center_x + (self.radius // 2 - 20) * math.cos(angle)
            y = self.center_y + (self.radius // 2 - 20) * math.sin(angle)
            draw_text(surface, number, 30, GREEN, x, y)
            
            # Draw red indicator at 4 when suspicion is high
            if suspicion_level > 80 and number == "4":
                pygame.draw.line(surface, RED, 
                               (self.center_x, self.center_y),
                               (x, y), 2)
        
        # Draw center pin
        pygame.draw.circle(surface, RED, (self.center_x, self.center_y), 10)
        
        # Draw instructions
        draw_text(surface, "A/D to rotate, ENTER to close", 30, WHITE, 
                 self.center_x, self.center_y + self.radius + 30)
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.outer_angle -= self.rotation_speed
        if keys[pygame.K_d]:
            self.outer_angle += self.rotation_speed
        
        # Keep angle within 0-360 range
        self.outer_angle %= 360
    
    def toggle(self):
        self.visible = not self.visible
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.visible = False

class SuspicionSystem:
    def __init__(self):
        self.suspicion = 0
        self.max_suspicion = 100
        self.increase_rate = 10
        self.decrease_rate = 0.2
        self.high_suspicion_threshold = 80
        self.effective_suspicion = 0
    
    def update(self, dt, is_being_chased):
        if is_being_chased:
            self.suspicion = min(self.max_suspicion, self.suspicion + self.increase_rate * dt)
        else:
            self.suspicion = max(0, self.suspicion - self.decrease_rate * dt)
        
        self.effective_suspicion = self.effective_suspicion * 0.9 + self.suspicion * 0.1
    
    def get_suspicion_modifier(self):
        return 1.0 + (self.suspicion / self.max_suspicion) * 0.5
    
    def draw_effects(self, surface):
        if self.suspicion > self.high_suspicion_threshold:
            intensity = min(1.0, (self.suspicion - self.high_suspicion_threshold) / 
                        (self.max_suspicion - self.high_suspicion_threshold))
            
            border_size = int(10 * intensity)
            if border_size > 0:
                border = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(border, (255, 0, 0, int(150 * intensity)), 
                                (0, 0, SCREEN_WIDTH, border_size))
                pygame.draw.rect(border, (255, 0, 0, int(150 * intensity)), 
                                (0, SCREEN_HEIGHT - border_size, SCREEN_WIDTH, border_size))
                pygame.draw.rect(border, (255, 0, 0, int(150 * intensity)), 
                                (0, 0, border_size, SCREEN_HEIGHT))
                pygame.draw.rect(border, (255, 0, 0, int(150 * intensity)), 
                                (SCREEN_WIDTH - border_size, 0, border_size, SCREEN_HEIGHT))
                surface.blit(border, (0, 0))
        
        meter_width = 200
        meter_height = 20
        meter_x = SCREEN_WIDTH - meter_width - 20
        meter_y = 20
        
        pygame.draw.rect(surface, (50, 50, 50), (meter_x, meter_y, meter_width, meter_height))
        pygame.draw.rect(surface, (255, 0, 0), 
                        (meter_x, meter_y, meter_width * (self.suspicion / self.max_suspicion), meter_height))
        pygame.draw.rect(surface, WHITE, (meter_x, meter_y, meter_width, meter_height), 2)
        
        font = pygame.font.Font(None, 24)
        text = font.render("SUSPICION", True, WHITE)
        surface.blit(text, (meter_x, meter_y - 25))

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x, y))

class Sign(pygame.sprite.Sprite):
    def __init__(self, x, y, normal_text, high_suspicion_text=None):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(YELLOW)
        pygame.draw.rect(self.image, BLACK, (0, 0, 40, 60), 2)
        draw_text(self.image, "!", 30, BLACK, 20, 30)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.normal_text = normal_text
        self.high_suspicion_text = high_suspicion_text if high_suspicion_text else normal_text
        self.interact_rect = pygame.Rect(x - 50, y - 50, 140, 160)
    
    def get_text(self, suspicion_level, high_threshold=80):
        if suspicion_level > high_threshold and self.high_suspicion_text:
            return self.high_suspicion_text
        return self.normal_text

class MusicPlayer:
    def __init__(self, music_file):
        pygame.mixer.init()
        self.music_file = music_file
        self.is_playing = False

    def play(self):
        if not self.is_playing:
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.play(-1)
            self.is_playing = True

    def stop(self):
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume)

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
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
        
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        
        old_pos = self.pos.copy()
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.pos.x, self.pos.y = self.rect.center
        
        return old_pos

class Player(AnimatedSprite):
    def __init__(self, x, y):
        self.sprite_width = 80
        self.sprite_height = 120
        self.cols = 2
        self.rows = 4
        
        sprite_sheet = self.load_sprite_sheet("player.png", self.cols, self.rows)
        
        self.animations = {
            "down": sprite_sheet[0:2],
            "left": sprite_sheet[2:4],
            "right": sprite_sheet[4:6],
            "up": sprite_sheet[6:8]
        }
        
        super().__init__((x, y), self.animations["down"])
        self.current_animation = "down"
        self.last_direction = "down"
        self.can_interact = False
        self.near_sign = None
        self.stun_cooldown = 0
        self.stun_radius = 150
        self.stun_duration = 3.0
        self.stun_cooldown_time = 5.0
        
    def load_sprite_sheet(self, filename, cols, rows):
        try:
            full_path = os.path.join("Sprites", filename)
            sprite_sheet = pygame.image.load(full_path).convert_alpha()
        except:
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
    
    def update(self, dt, walls, signs, mobs=None):
        keys = pygame.key.get_pressed()
        move_vec = pygame.Vector2(0, 0)
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_vec.y -= 1
            self.last_direction = "up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_vec.y += 1
            self.last_direction = "down"
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_vec.x -= 1
            self.last_direction = "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_vec.x += 1
            self.last_direction = "right"
            
        if keys[pygame.K_p] and self.stun_cooldown <= 0 and mobs:
            self.stun_nearby_mobs(mobs)
            self.stun_cooldown = self.stun_cooldown_time
            
        self.direction = move_vec
        
        if move_vec.length() > 0:
            if abs(move_vec.x) > abs(move_vec.y):
                self.current_animation = "left" if move_vec.x < 0 else "right"
            else:
                self.current_animation = "up" if move_vec.y < 0 else "down"
            
            if self.frames != self.animations[self.current_animation]:
                self.frames = self.animations[self.current_animation]
                self.current_frame = 0
        else:
            if self.frames != self.animations[self.last_direction]:
                self.frames = self.animations[self.last_direction]
                self.current_frame = 0
        
        old_pos = super().update(dt)
        
        wall_collisions = pygame.sprite.spritecollide(self, walls, False)
        if wall_collisions:
            self.pos = old_pos
            self.rect.center = self.pos
        
        self.can_interact = False
        self.near_sign = None
        for sign in signs:
            if self.rect.colliderect(sign.interact_rect):
                self.can_interact = True
                self.near_sign = sign
                break
        
        if self.stun_cooldown > 0:
            self.stun_cooldown -= dt
    
    def stun_nearby_mobs(self, mobs):
        for mob in mobs:
            dx = mob.rect.centerx - self.rect.centerx
            dy = mob.rect.centery - self.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance <= self.stun_radius:
                mob.get_stunned(self.stun_duration)

class Mob(AnimatedSprite):
    def __init__(self, x, y):
        self.sprite_width = 64
        self.sprite_height = 64
        self.cols = 4
        self.rows = 1

        self.chasing = False
        self.chase_distance = 200
        self.base_speed = 100
        self.base_chase_speed = 150
        self.speed = self.base_speed
        self.chase_speed = self.base_chase_speed
        
        self.stunned = False
        self.stun_timer = 0
        self.normal_color = (255, 255, 255)
        self.stunned_color = (100, 100, 255)
        
        sprite_sheet = self.load_sprite_sheet("Golem_Run.png", self.cols, self.rows)
        
        self.animations = {
            "right": sprite_sheet
        }
        
        super().__init__((x, y), self.animations["right"])

    def load_sprite_sheet(self, filename, cols, rows):
        try:
            full_path = os.path.join("Sprites", filename)
            sprite_sheet = pygame.image.load(full_path).convert_alpha()
        except:
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
    
    def update_speed(self, suspicion_modifier):
        self.speed = self.base_speed * suspicion_modifier
        self.chase_speed = self.base_chase_speed * suspicion_modifier
        
        if self.chasing and not self.stunned:
            self.speed = self.chase_speed
        elif not self.stunned:
            self.speed = self.base_speed * suspicion_modifier
    
    def update(self, dt, player, walls):
        if self.stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.stunned = False
                self.speed = self.base_speed
                for frame in self.frames:
                    frame.fill(self.normal_color, special_flags=pygame.BLEND_MULT)
        
        if not self.stunned:
            if not self.chasing:
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist < self.chase_distance:
                    self.chasing = True
                    self.speed = self.chase_speed
            else:
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist > 0:
                    dx /= dist
                    dy /= dist
                    self.direction = pygame.Vector2(dx, dy)
                
                if dist > self.chase_distance * 1.5:
                    self.chasing = False
                    self.speed = self.base_speed
        
            old_pos = super().update(dt)
            
            wall_collisions = pygame.sprite.spritecollide(self, walls, False)
            if wall_collisions:
                self.pos = old_pos
                self.rect.center = self.pos
            
            if self.rect.top > SCREEN_HEIGHT + 15 or self.rect.left < -15 or self.rect.right > SCREEN_WIDTH + 15:
                self.rect.x = random.randrange(SCREEN_WIDTH - self.sprite_width)
                self.rect.y = random.randrange(-100, -50)
                self.chasing = False
                self.speed = self.base_speed
    
    def get_stunned(self, duration):
        self.stunned = True
        self.stun_timer = duration
        self.speed = 0
        for frame in self.frames:
            frame.fill(self.stunned_color, special_flags=pygame.BLEND_MULT)

def main():
    if not show_start_screen():
        return
    
    # Load the tmx map
    tmx_data = pytmx.util_pygame.load_pygame(os.path.join("Maps", "TLSBNR_MainMap.tmx"))
    
    suspicion_system = SuspicionSystem()
    wheel_cipher = WheelCipher()
    
    running = True
    while running:
        all_sprites = pygame.sprite.Group()
        walls = pygame.sprite.Group()
        signs = pygame.sprite.Group()

        #wall_positions = [
        #    (100, 100, 200, 50),
        #    (400, 300, 50, 200),
        #    (700, 200, 200, 50),
        #    (900, 500, 300, 50)
        #]

        #for x, y, w, h in wall_positions:
        #    wall = Wall(x, y, w, h)
        #    all_sprites.add(wall)
        #    walls.add(wall)

        sign1 = Sign(300, 200, 
                    "Welcome to Lone Voyager! Press O to interact with signs.",
                    "They're watching you! Be careful!")
        sign2 = Sign(800, 400,
                    "Press P to stun nearby enemies when they chase you!",
                    "They're getting faster! Use your stun wisely!")
        all_sprites.add(sign1)
        all_sprites.add(sign2)
        signs.add(sign1)
        signs.add(sign2)

        player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        all_sprites.add(player)

        default_music = MusicPlayer("2.Aria of the Soul(P4).mp3")
        chase_music = MusicPlayer("Hollow Knight OST.mp3")
        default_music.play()
        default_music.set_volume(1.0)
        
        mobs = pygame.sprite.Group()
        for i in range(5):
            mob = Mob(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            all_sprites.add(mob)
            mobs.add(mob)

        playing = True
        dt = 0
        chase_music_playing = False
        
        while playing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        playing = False
                        running = False
                    elif event.key == pygame.K_o and player.can_interact:
                        sign_text = player.near_sign.get_text(suspicion_system.suspicion)
                        if not show_message_screen(sign_text):
                            playing = False
                            running = False
                    elif event.key == pygame.K_i:
                        wheel_cipher.toggle()
                    elif wheel_cipher.visible and event.key == pygame.K_RETURN:
                        wheel_cipher.toggle()
            
            any_chasing = False
            for mob in mobs:
                mob.update(dt, player, walls)
                if mob.chasing and not mob.stunned:
                    any_chasing = True
            
            suspicion_system.update(dt, any_chasing)
            suspicion_modifier = suspicion_system.get_suspicion_modifier()
            for mob in mobs:
                mob.update_speed(suspicion_modifier)
            
            if not wheel_cipher.visible:
                player.update(dt, walls, signs, mobs)
            else:
                wheel_cipher.update()
            
            if any_chasing:
                if not chase_music_playing:
                    default_music.stop()
                    chase_music.play()
                    chase_music.set_volume(1.0)
                    chase_music_playing = True
            else:
                if chase_music_playing:
                    chase_music.stop()
                    default_music.play()
                    chase_music_playing = False
            
            collisions = pygame.sprite.spritecollide(player, mobs, False)
            if collisions:
                playing = False
            
            screen.fill(BLACK)
            draw_map(screen, tmx_data)
            all_sprites.draw(screen)
            
            if player.can_interact:
                draw_text(screen, "Press O to read", 24, WHITE, player.rect.centerx, player.rect.top - 20)
            
            suspicion_system.draw_effects(screen)
            wheel_cipher.draw(screen, suspicion_system.suspicion)
            
            if player.stun_cooldown > 0:
                cooldown_width = 200 * (1 - player.stun_cooldown / player.stun_cooldown_time)
                pygame.draw.rect(screen, RED, (10, 10, cooldown_width, 20))
                pygame.draw.rect(screen, WHITE, (10, 10, 200, 20), 2)
                draw_text(screen, "Stun Cooldown", 20, WHITE, 110, 20)
            elif not wheel_cipher.visible:
                draw_text(screen, "Press P to stun nearby enemies", 24, WHITE, SCREEN_WIDTH // 2, 30)
            
            if wheel_cipher.visible:
                draw_text(screen, "Press I to close cipher wheel", 24, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
            else:
                draw_text(screen, "Press I to open cipher wheel", 24, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
            
            pygame.display.flip()
            dt = clock.tick(FPS) / 1000
        
        default_music.stop()
        if chase_music_playing:
            chase_music.stop()
        
        if running:
            running = show_game_over_screen()

    pygame.quit()

if __name__ == "__main__":
    main()
