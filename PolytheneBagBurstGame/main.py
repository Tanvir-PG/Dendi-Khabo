"""
=============================================================================
  THE GREAT PLASTIC BAG BLASTER (Polythene Bag Pop Game)
  A Funny, Cartoon-Style 2D Animated Arcade Game in Pygame
=============================================================================
Controls:
  - HOLD [SPACEBAR]   : Blow air into the polythene bag!
  - RELEASE [SPACEBAR]: Stop blowing (pressure will slowly leak)
  - PRESS [R]         : Restart game
  - PRESS [M]         : Toggle Sound (Mute/Unmute)
=============================================================================
"""

import sys
import os
import math
import random
import struct
import wave
import pygame

# Initialize Pygame and Mixer
pygame.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    AUDIO_AVAILABLE = True
except Exception:
    AUDIO_AVAILABLE = False

# ---------------------------------------------------------------------------
# CONSTANTS & CONFIGURATION
# ---------------------------------------------------------------------------
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "The Great Bag Buster! - 2D Cartoon Arcade"

# Color Palette (Vibrant & Warm Cartoon Aesthetics)
COLOR_BG_WALL = (248, 241, 227)        # Warm beige classroom wall
COLOR_BG_WAINSCOT = (222, 207, 182)    # Lower wall trim
COLOR_WOOD_DARK = (92, 58, 33)         # Dark wood borders
COLOR_WOOD_LIGHT = (168, 119, 74)      # Desk top wood
COLOR_WOOD_MID = (133, 89, 52)         # Desk structure
COLOR_CHALKBOARD = (34, 76, 56)        # Deep green chalkboard
COLOR_CHALK_WHITE = (235, 245, 240)    # Soft chalk white
COLOR_CHALK_YELLOW = (255, 235, 130)   # Chalk yellow
COLOR_CHALK_PINK = (255, 175, 190)     # Chalk pink
COLOR_SHIRT = (41, 98, 255)            # Royal blue school uniform
COLOR_SHIRT_COLLAR = (245, 245, 250)   # White collar
COLOR_TIE = (220, 38, 38)              # Crimson red tie
COLOR_SKIN = (255, 213, 179)           # Cartoon skin tone
COLOR_SKIN_SHADOW = (235, 185, 148)    # Skin shading
COLOR_CHEEKS_NORMAL = (255, 170, 160)  # Gentle blush
COLOR_CHEEKS_BLOW = (255, 75, 75)      # Strained red cheeks
COLOR_HAIR = (55, 35, 25)              # Dark messy hair
COLOR_BAG_TINT = (100, 210, 255)       # Cyan translucent polythene
COLOR_BAG_OUTLINE = (50, 160, 220)     # Polythene perimeter
COLOR_SWEAT = (140, 220, 255)          # Sweat drop blue

# ---------------------------------------------------------------------------
# PROCEDURAL SOUND GENERATOR (Zero external asset dependencies!)
# Generates sweet 8-bit / 16-bit cartoon sound effects using Python's standard wave library.
# ---------------------------------------------------------------------------
SOUNDS = {}

def generate_procedural_sounds():
    """Generates procedural WAV sound files so the game runs immediately with full audio."""
    if not AUDIO_AVAILABLE:
        return

    sound_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets_audio")
    os.makedirs(sound_dir, exist_ok=True)

    blow_path = os.path.join(sound_dir, "blow.wav")
    pop_path = os.path.join(sound_dir, "pop.wav")
    win_path = os.path.join(sound_dir, "win.wav")

    # 1. Blow Sound (Airy whooshing breath)
    if not os.path.exists(blow_path):
        sample_rate = 44100
        duration = 0.6
        num_samples = int(sample_rate * duration)
        with wave.open(blow_path, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            frames = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                env = math.sin(math.pi * (i / num_samples))
                # Layered noise + soft low sine oscillation
                noise = (random.random() * 2.0 - 1.0) * 0.4
                tone = math.sin(2.0 * math.pi * 140.0 * t) * 0.3
                sample_val = int((noise + tone) * env * 14000.0)
                sample_val = max(-32768, min(32767, sample_val))
                frames.extend(struct.pack("<h", sample_val))
            wav_file.writeframes(frames)

    # 2. POP Sound (Punchy comic explosion with sudden snap & low thud)
    if not os.path.exists(pop_path):
        sample_rate = 44100
        duration = 0.5
        num_samples = int(sample_rate * duration)
        with wave.open(pop_path, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            frames = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                # Sharp envelope with sudden attack and fast decay
                decay = math.exp(-14.0 * t)
                # Rapid pitch slide from 600Hz down to 50Hz + white noise crack
                freq = 550.0 * math.exp(-25.0 * t) + 60.0
                tone = math.sin(2.0 * math.pi * freq * t)
                noise = (random.random() * 2.0 - 1.0) * math.exp(-35.0 * t) * 1.5
                sample_val = int((tone + noise) * decay * 28000.0)
                sample_val = max(-32768, min(32767, sample_val))
                frames.extend(struct.pack("<h", sample_val))
            wav_file.writeframes(frames)

    # 3. Win Victory Fanfare (Happy rising arpeggio C5 -> E5 -> G5 -> C6!)
    if not os.path.exists(win_path):
        sample_rate = 44100
        duration = 1.0
        num_samples = int(sample_rate * duration)
        notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
        note_len = duration / len(notes)
        with wave.open(win_path, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            frames = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                note_idx = min(len(notes) - 1, int(t / note_len))
                freq = notes[note_idx]
                t_in_note = (t % note_len) / note_len
                env = math.sin(math.pi * t_in_note) ** 0.5
                val = math.sin(2.0 * math.pi * freq * t) * 0.6
                harmonic = math.sin(4.0 * math.pi * freq * t) * 0.2
                sample_val = int((val + harmonic) * env * 22000.0)
                sample_val = max(-32768, min(32767, sample_val))
                frames.extend(struct.pack("<h", sample_val))
            wav_file.writeframes(frames)

    try:
        SOUNDS["blow"] = pygame.mixer.Sound(blow_path)
        SOUNDS["pop"] = pygame.mixer.Sound(pop_path)
        SOUNDS["win"] = pygame.mixer.Sound(win_path)
        SOUNDS["blow"].set_volume(0.45)
        SOUNDS["pop"].set_volume(0.9)
        SOUNDS["win"].set_volume(0.7)
    except Exception as e:
        print(f"Audio init warning: {e}")

# ---------------------------------------------------------------------------
# VISUAL PARTICLES (Air, Sweat, Plastic Shreds, Confetti)
# ---------------------------------------------------------------------------
class AirParticle:
    """Air bubbles emitted from the mouth into the polythene bag."""
    def __init__(self, start_x, start_y, target_x, target_y):
        self.x = start_x + random.uniform(-4, 4)
        self.y = start_y + random.uniform(-4, 4)
        angle = math.atan2(target_y - start_y, target_x - start_x) + random.uniform(-0.35, 0.35)
        speed = random.uniform(3.5, 7.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = random.uniform(2.5, 6.0)
        self.alpha = 220
        self.life = random.randint(18, 30)
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.94
        self.vy *= 0.94
        self.life -= 1
        self.alpha = int(220 * (self.life / self.max_life))

    def draw(self, surface):
        if self.life > 0 and self.alpha > 0:
            bubble_surf = pygame.Surface((int(self.radius * 2 + 4), int(self.radius * 2 + 4)), pygame.SRCALPHA)
            pygame.draw.circle(bubble_surf, (255, 255, 255, self.alpha), 
                               (int(self.radius + 2), int(self.radius + 2)), int(self.radius))
            pygame.draw.circle(bubble_surf, (160, 230, 255, int(self.alpha * 0.7)), 
                               (int(self.radius + 2), int(self.radius + 2)), int(self.radius), 1)
            surface.blit(bubble_surf, (self.x - self.radius - 2, self.y - self.radius - 2))


class SweatDrop:
    """Cartoon sweat drops that fly off the schoolboy's face when pressure is intense."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(1.5, 4.0)
        self.vy = random.uniform(-4.0, -1.0)
        self.radius = random.uniform(3.0, 5.0)
        self.life = 25

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.28  # gravity
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, COLOR_SWEAT, (int(self.x), int(self.y)), int(self.radius))
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x - 1), int(self.y - 1)), 1)


class PlasticShred:
    """Torn polythene fragments flying in all directions upon bursting."""
    def __init__(self, origin_x, origin_y):
        self.x = origin_x
        self.y = origin_y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(5.0, 16.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - random.uniform(2.0, 6.0)
        self.size = random.uniform(8.0, 22.0)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-18.0, 18.0)
        self.color = random.choice([
            (120, 220, 255, 220),
            (80, 190, 245, 210),
            (180, 240, 255, 230),
            (255, 255, 255, 240),
            (255, 180, 210, 200)
        ])
        self.life = random.randint(55, 85)
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.35  # gravity
        self.vx *= 0.97  # air resistance
        self.rotation += self.rot_speed
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(self.color[3] * (self.life / self.max_life))
        shred_surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pts = [
            (self.size, 2),
            (self.size * 1.8, self.size * 0.7),
            (self.size * 1.3, self.size * 1.7),
            (self.size * 0.3, self.size * 1.4),
            (self.size * 0.1, self.size * 0.5)
        ]
        color_with_alpha = (self.color[0], self.color[1], self.color[2], alpha)
        pygame.draw.polygon(shred_surf, color_with_alpha, pts)
        pygame.draw.polygon(shred_surf, (255, 255, 255, alpha), pts, 1)

        rotated = pygame.transform.rotate(shred_surf, self.rotation)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rect.topleft)


class Confetti:
    """Vibrant celebratory confetti raining down on victory."""
    def __init__(self):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(-200, -10)
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(2.5, 5.5)
        self.width = random.uniform(6.0, 12.0)
        self.height = random.uniform(4.0, 8.0)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-8.0, 8.0)
        self.color = random.choice([
            (255, 82, 82), (255, 177, 66), (255, 218, 121),
            (52, 231, 228), (126, 255, 245), (109, 33, 79),
            (24, 220, 255), (180, 110, 255), (46, 213, 115)
        ])

    def update(self):
        self.x += self.vx + math.sin(self.y * 0.05) * 0.8
        self.y += self.vy
        self.rotation += self.rot_speed
        if self.y > SCREEN_HEIGHT + 20:
            self.y = random.uniform(-50, -10)
            self.x = random.uniform(0, SCREEN_WIDTH)

    def draw(self, surface):
        conf_surf = pygame.Surface((int(self.width), int(self.height)), pygame.SRCALPHA)
        conf_surf.fill(self.color)
        rotated = pygame.transform.rotate(conf_surf, self.rotation)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rect.topleft)


# ---------------------------------------------------------------------------
# MAIN GAME CLASS
# ---------------------------------------------------------------------------
class PlasticBagBusterGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Fonts
        self.font_title = pygame.font.SysFont("Comic Sans MS, Segoe UI, Arial", 44, bold=True)
        self.font_header = pygame.font.SysFont("Comic Sans MS, Segoe UI, Arial", 28, bold=True)
        self.font_body = pygame.font.SysFont("Comic Sans MS, Segoe UI, Arial", 18, bold=True)
        self.font_small = pygame.font.SysFont("Comic Sans MS, Segoe UI, Arial", 14, bold=True)
        self.font_pop = pygame.font.SysFont("Impact, Comic Sans MS, Arial Black", 76, bold=True)

        # Procedural Audio
        generate_procedural_sounds()
        self.sound_muted = False
        self.blow_channel = None

        # Game State
        self.reset_game()

    def reset_game(self):
        """Reset or initialize all gameplay variables."""
        self.pressure = 0.0           # 0.0 to 100.0%
        self.is_blowing = False
        self.game_won = False
        self.burst_trigger = False
        self.burst_timer = 0
        self.total_time = 0.0
        self.blow_duration = 0.0
        self.shake_intensity = 0.0

        # Character animation timers
        self.anim_tick = 0
        self.blink_timer = random.randint(120, 240)
        self.is_blinking = False

        # Particle Systems
        self.air_particles = []
        self.sweat_particles = []
        self.plastic_shreds = []
        self.confetti_list = [Confetti() for _ in range(110)]

        # Classroom clock animation
        self.clock_angle = 0.0

        # Play Again Button Rect
        self.btn_restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 150, 240, 52)
        self.btn_hover = False

    def play_sound(self, name):
        """Plays sound safely if audio is working and not muted."""
        if not self.sound_muted and AUDIO_AVAILABLE and name in SOUNDS:
            try:
                SOUNDS[name].play()
            except Exception:
                pass

    # -----------------------------------------------------------------------
    # INPUT HANDLING
    # -----------------------------------------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_won:
                    self.is_blowing = True
                    self.play_sound("blow")

                elif event.key == pygame.K_r:
                    self.reset_game()

                elif event.key == pygame.K_m:
                    self.sound_muted = not self.sound_muted

                elif event.key == pygame.K_ESCAPE:
                    self.running = False

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.is_blowing = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if self.game_won and self.btn_restart_rect.collidepoint(mouse_pos):
                    self.reset_game()

    # -----------------------------------------------------------------------
    # GAMEPLAY LOGIC & UPDATE
    # -----------------------------------------------------------------------
    def update(self):
        self.anim_tick += 1
        self.clock_angle += 0.8  # Classroom clock second hand ticks

        # Blinking logic
        self.blink_timer -= 1
        if self.blink_timer <= 0:
            self.is_blinking = not self.is_blinking
            self.blink_timer = 8 if self.is_blinking else random.randint(120, 260)

        if not self.game_won:
            self.total_time += 1.0 / FPS

            if self.is_blowing:
                self.blow_duration += 1.0 / FPS
                # Rate of inflation: increases smoothly
                inflation_speed = 0.42
                self.pressure += inflation_speed

                # Emit air particles into the bag
                mouth_x = 350
                mouth_y = 358
                target_x = 480 + self.pressure * 0.8
                target_y = 345
                if self.anim_tick % 2 == 0:
                    for _ in range(2):
                        self.air_particles.append(AirParticle(mouth_x, mouth_y, target_x, target_y))

                # Emit comedic sweat drops when pressure is high
                if self.pressure > 70.0 and random.random() < 0.28:
                    self.sweat_particles.append(SweatDrop(280 + random.uniform(-10, 10), 305))

                # Screen / bag shake increases as pressure reaches max
                if self.pressure > 65.0:
                    self.shake_intensity = (self.pressure - 65.0) * 0.18
                else:
                    self.shake_intensity = 0.0

            else:
                # Slight deflation if player releases SPACEBAR (pressure slowly leaks)
                if self.pressure > 0:
                    self.pressure = max(0.0, self.pressure - 0.20)
                self.shake_intensity = max(0.0, self.shake_intensity - 0.25)

            # Check for 100% burst threshold
            if self.pressure >= 100.0:
                self.pressure = 100.0
                self.trigger_burst()

        else:
            # Game won celebration update
            self.burst_timer += 1
            for conf in self.confetti_list:
                conf.update()

        # Update Air Particles
        for p in self.air_particles[:]:
            p.update()
            if p.life <= 0:
                self.air_particles.remove(p)

        # Update Sweat Drops
        for s in self.sweat_particles[:]:
            s.update()
            if s.life <= 0:
                self.sweat_particles.remove(s)

        # Update Plastic Shreds (Burst shrapnel)
        for shred in self.plastic_shreds[:]:
            shred.update()
            if shred.life <= 0:
                self.plastic_shreds.remove(shred)

        # Check button hover
        mouse_pos = pygame.mouse.get_pos()
        self.btn_hover = self.btn_restart_rect.collidepoint(mouse_pos)

    def trigger_burst(self):
        """Trigger the dramatic comic bursting sequence & victory."""
        self.game_won = True
        self.burst_trigger = True
        self.burst_timer = 0
        self.play_sound("pop")
        self.play_sound("win")

        # Spawn comic plastic shreds radiating from bag center
        bag_center_x = 510
        bag_center_y = 330
        for _ in range(75):
            self.plastic_shreds.append(PlasticShred(bag_center_x, bag_center_y))

    # -----------------------------------------------------------------------
    # DRAWING ROUTINES: CLASSROOM ENVIRONMENT
    # -----------------------------------------------------------------------
    def draw_classroom_background(self):
        # 1. Warm Wall Background
        self.screen.fill(COLOR_BG_WALL)

        # 2. Lower Wall Wainscoting (Wooden Dado)
        wainscot_y = 440
        pygame.draw.rect(self.screen, COLOR_BG_WAINSCOT, (0, wainscot_y, SCREEN_WIDTH, SCREEN_HEIGHT - wainscot_y))
        pygame.draw.rect(self.screen, COLOR_WOOD_DARK, (0, wainscot_y, SCREEN_WIDTH, 12))
        for x in range(0, SCREEN_WIDTH, 70):
            pygame.draw.line(self.screen, (208, 192, 168), (x, wainscot_y + 12), (x, SCREEN_HEIGHT), 2)

        # 3. Big Green Chalkboard
        board_rect = pygame.Rect(40, 45, 520, 220)
        # Wooden Frame
        pygame.draw.rect(self.screen, COLOR_WOOD_MID, (board_rect.x - 12, board_rect.y - 12, board_rect.w + 24, board_rect.h + 24), border_radius=6)
        pygame.draw.rect(self.screen, COLOR_WOOD_DARK, (board_rect.x - 12, board_rect.y - 12, board_rect.w + 24, board_rect.h + 24), 3, border_radius=6)
        # Green Surface
        pygame.draw.rect(self.screen, COLOR_CHALKBOARD, board_rect, border_radius=4)

        # Chalk Doodles & Text
        txt_subj = self.font_body.render("LESSON: PNEUMATICS & AIR PRESSURE", True, COLOR_CHALK_YELLOW)
        txt_goal = self.font_small.render("MISSION: INFLATE BAG UNTIL IT BURSTS! 🎈💥", True, COLOR_CHALK_WHITE)
        txt_formula = self.font_small.render("P = F / A   |   Target = 100% POP!", True, COLOR_CHALK_PINK)
        self.screen.blit(txt_subj, (board_rect.x + 22, board_rect.y + 20))
        self.screen.blit(txt_goal, (board_rect.x + 22, board_rect.y + 55))
        self.screen.blit(txt_formula, (board_rect.x + 22, board_rect.y + 85))

        # Funny Chalk Stick Figure Doodle
        doodle_x = board_rect.x + 390
        doodle_y = board_rect.y + 130
        pygame.draw.circle(self.screen, COLOR_CHALK_WHITE, (doodle_x, doodle_y), 16, 2)  # Head
        pygame.draw.line(self.screen, COLOR_CHALK_WHITE, (doodle_x, doodle_y + 16), (doodle_x, doodle_y + 48), 2)  # Body
        pygame.draw.line(self.screen, COLOR_CHALK_WHITE, (doodle_x - 18, doodle_y + 28), (doodle_x + 18, doodle_y + 28), 2)  # Arms
        pygame.draw.line(self.screen, COLOR_CHALK_WHITE, (doodle_x, doodle_y + 48), (doodle_x - 14, doodle_y + 72), 2)  # Legs
        pygame.draw.line(self.screen, COLOR_CHALK_WHITE, (doodle_x, doodle_y + 48), (doodle_x + 14, doodle_y + 72), 2)
        # Giant balloon in stick figure's hand
        pygame.draw.circle(self.screen, COLOR_CHALK_PINK, (doodle_x + 48, doodle_y + 20), 22, 2)
        pygame.draw.line(self.screen, COLOR_CHALK_PINK, (doodle_x + 18, doodle_y + 28), (doodle_x + 30, doodle_y + 22), 2)
        txt_boom = self.font_small.render("BOOM?!", True, COLOR_CHALK_YELLOW)
        self.screen.blit(txt_boom, (doodle_x + 30, doodle_y + 48))

        # Chalk Tray & Chalk Sticks
        tray_rect = pygame.Rect(board_rect.x + 20, board_rect.bottom + 2, 160, 8)
        pygame.draw.rect(self.screen, (70, 45, 25), tray_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), (tray_rect.x + 10, tray_rect.y - 4, 18, 5))
        pygame.draw.rect(self.screen, COLOR_CHALK_YELLOW, (tray_rect.x + 35, tray_rect.y - 4, 16, 5))
        # Eraser
        pygame.draw.rect(self.screen, (60, 60, 60), (tray_rect.x + 65, tray_rect.y - 7, 34, 8), border_radius=2)
        pygame.draw.rect(self.screen, (200, 180, 140), (tray_rect.x + 65, tray_rect.y - 10, 34, 4))

        # 4. Animated Classroom Clock (Top Right)
        clock_cx = 810
        clock_cy = 100
        clock_r = 44
        pygame.draw.circle(self.screen, (240, 240, 245), (clock_cx, clock_cy), clock_r)
        pygame.draw.circle(self.screen, COLOR_WOOD_DARK, (clock_cx, clock_cy), clock_r, 5)
        pygame.draw.circle(self.screen, (40, 40, 40), (clock_cx, clock_cy), 4)
        # Clock ticks
        for hour in range(12):
            ang = math.radians(hour * 30)
            hx1 = clock_cx + math.sin(ang) * (clock_r - 9)
            hy1 = clock_cy - math.cos(ang) * (clock_r - 9)
            hx2 = clock_cx + math.sin(ang) * (clock_r - 3)
            hy2 = clock_cy - math.cos(ang) * (clock_r - 3)
            pygame.draw.line(self.screen, (60, 60, 60), (hx1, hy1), (hx2, hy2), 2)
        # Moving minute and second hands
        sec_ang = math.radians(self.clock_angle)
        sx = clock_cx + math.sin(sec_ang) * (clock_r - 10)
        sy = clock_cy - math.cos(sec_ang) * (clock_r - 10)
        pygame.draw.line(self.screen, (220, 40, 40), (clock_cx, clock_cy), (sx, sy), 2)

        min_ang = math.radians(self.clock_angle * 0.08)
        mx = clock_cx + math.sin(min_ang) * (clock_r - 16)
        my = clock_cy - math.cos(min_ang) * (clock_r - 16)
        pygame.draw.line(self.screen, (40, 40, 40), (clock_cx, clock_cy), (mx, my), 3)

        # 5. Motivational School Poster
        post_rect = pygame.Rect(600, 65, 150, 160)
        pygame.draw.rect(self.screen, (255, 252, 235), post_rect, border_radius=4)
        pygame.draw.rect(self.screen, (220, 210, 185), post_rect, 2, border_radius=4)
        # Pin
        pygame.draw.circle(self.screen, (220, 50, 50), (post_rect.centerx, post_rect.top + 10), 5)
        # Poster text
        p_txt1 = self.font_small.render("SCHOOL RULE:", True, (50, 50, 50))
        p_txt2 = self.font_body.render("NEVER", True, (220, 30, 30))
        p_txt3 = self.font_body.render("GIVE UP!", True, (220, 30, 30))
        p_txt4 = self.font_small.render("(OR POP IT!)", True, (80, 80, 120))
        self.screen.blit(p_txt1, (post_rect.x + 18, post_rect.y + 28))
        self.screen.blit(p_txt2, (post_rect.x + 40, post_rect.y + 54))
        self.screen.blit(p_txt3, (post_rect.x + 32, post_rect.y + 78))
        self.screen.blit(p_txt4, (post_rect.x + 28, post_rect.y + 115))

    # -----------------------------------------------------------------------
    # DRAWING ROUTINES: SCHOOL DESK & PROPS
    # -----------------------------------------------------------------------
    def draw_school_desk(self):
        # Desk Top Wooden Plank
        desk_top_y = 425
        desk_rect = pygame.Rect(120, desk_top_y, 480, 36)
        pygame.draw.rect(self.screen, COLOR_WOOD_LIGHT, desk_rect, border_radius=5)
        pygame.draw.rect(self.screen, COLOR_WOOD_DARK, desk_rect, 3, border_radius=5)
        # Wood bevel highlight
        pygame.draw.line(self.screen, (200, 155, 110), (desk_rect.x + 5, desk_top_y + 4), (desk_rect.right - 5, desk_top_y + 4), 2)

        # Desk Legs (Sturdy metal tubular legs)
        leg_color = (65, 75, 85)
        # Left Leg
        pygame.draw.rect(self.screen, leg_color, (160, desk_top_y + 36, 16, SCREEN_HEIGHT - (desk_top_y + 36)))
        pygame.draw.rect(self.screen, (40, 45, 55), (155, SCREEN_HEIGHT - 12, 26, 12), border_radius=3)
        # Right Leg
        pygame.draw.rect(self.screen, leg_color, (540, desk_top_y + 36, 16, SCREEN_HEIGHT - (desk_top_y + 36)))
        pygame.draw.rect(self.screen, (40, 45, 55), (535, SCREEN_HEIGHT - 12, 26, 12), border_radius=3)
        # Desk Front Panel
        pygame.draw.rect(self.screen, COLOR_WOOD_MID, (176, desk_top_y + 36, 364, 90))
        pygame.draw.rect(self.screen, COLOR_WOOD_DARK, (176, desk_top_y + 36, 364, 90), 2)

        # Desk Accessories: Books, Pencil Cup, Ruler
        # Stacked books
        pygame.draw.rect(self.screen, (220, 50, 50), (145, desk_top_y - 12, 60, 12), border_radius=2)
        pygame.draw.rect(self.screen, (50, 140, 220), (148, desk_top_y - 23, 54, 11), border_radius=2)
        pygame.draw.rect(self.screen, (255, 200, 50), (152, desk_top_y - 33, 46, 10), border_radius=2)

        # Pencil Cup & Stationery
        cup_x = 225
        cup_y = desk_top_y - 32
        pygame.draw.rect(self.screen, (240, 240, 245), (cup_x, cup_y, 24, 32), border_radius=3)
        pygame.draw.rect(self.screen, (100, 100, 100), (cup_x, cup_y, 24, 32), 2, border_radius=3)
        # Pencils sticking out
        pygame.draw.line(self.screen, (240, 180, 40), (cup_x + 6, cup_y + 6), (cup_x + 2, cup_y - 16), 4)
        pygame.draw.line(self.screen, (220, 50, 50), (cup_x + 12, cup_y + 6), (cup_x + 12, cup_y - 20), 4)
        pygame.draw.line(self.screen, (50, 180, 80), (cup_x + 18, cup_y + 6), (cup_x + 24, cup_y - 14), 4)

    # -----------------------------------------------------------------------
    # DRAWING ROUTINES: THE ANIMATED CARTOON SCHOOLBOY
    # -----------------------------------------------------------------------
    def draw_schoolboy(self):
        # Base anchor coordinates for character
        bx = 270
        by = 310

        # Shake and breathing offsets
        shake_x = 0
        shake_y = 0
        if self.shake_intensity > 0:
            shake_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            shake_y = random.uniform(-self.shake_intensity, self.shake_intensity)

        breath_bob = math.sin(self.anim_tick * 0.1) * 2.0 if not self.is_blowing else 1.0
        bx += shake_x
        by += shake_y + breath_bob

        # --- A. BODY / UNIFORM ---
        # Blue school shirt torso
        torso_rect = pygame.Rect(bx - 42, by + 50, 84, 85)
        pygame.draw.rect(self.screen, COLOR_SHIRT, torso_rect, border_radius=12)
        pygame.draw.rect(self.screen, (25, 60, 160), torso_rect, 3, border_radius=12)

        # White Collar
        collar_pts = [
            (bx - 26, by + 50),
            (bx, by + 74),
            (bx + 26, by + 50),
            (bx + 14, by + 50),
            (bx, by + 62),
            (bx - 14, by + 50)
        ]
        pygame.draw.polygon(self.screen, COLOR_SHIRT_COLLAR, collar_pts)
        pygame.draw.polygon(self.screen, (200, 200, 210), collar_pts, 2)

        # Red School Tie
        tie_pts = [
            (bx - 7, by + 68),
            (bx + 7, by + 68),
            (bx + 10, by + 115),
            (bx, by + 126),
            (bx - 10, by + 115)
        ]
        pygame.draw.polygon(self.screen, COLOR_TIE, tie_pts)
        pygame.draw.polygon(self.screen, (160, 20, 20), tie_pts, 2)

        # --- B. ARMS & HANDS ---
        if self.game_won:
            # VICTORY POSE: Arms raised high in joy ("\o/")
            # Left Arm Up
            pygame.draw.line(self.screen, COLOR_SHIRT, (bx - 36, by + 65), (bx - 65, by + 10), 16)
            pygame.draw.circle(self.screen, COLOR_SKIN, (int(bx - 65), int(by + 10)), 12)  # Left fist
            # Right Arm Up
            pygame.draw.line(self.screen, COLOR_SHIRT, (bx + 36, by + 65), (bx + 65, by + 10), 16)
            pygame.draw.circle(self.screen, COLOR_SKIN, (int(bx + 65), int(by + 10)), 12)  # Right fist
        else:
            # BLOWING / HOLDING POSE: Arms gripping the bag handles in front of lips
            # Left Arm to bag neck
            pygame.draw.line(self.screen, COLOR_SHIRT, (bx - 36, by + 68), (bx + 30, by + 78), 15)
            # Right Arm to bag neck
            pygame.draw.line(self.screen, COLOR_SHIRT, (bx + 20, by + 72), (bx + 68, by + 65), 15)
            # Hands gripping the bag knot
            pygame.draw.circle(self.screen, COLOR_SKIN, (int(bx + 52), int(by + 64)), 10)
            pygame.draw.circle(self.screen, COLOR_SKIN, (int(bx + 58), int(by + 60)), 9)

        # --- C. HEAD & FACE ---
        head_cx = int(bx)
        head_cy = int(by)
        head_radius = 42

        # Strained face turns increasingly pinkish-red as pressure rises
        current_skin = COLOR_SKIN
        if self.is_blowing:
            strain_factor = min(1.0, self.pressure / 100.0)
            r = int(COLOR_SKIN[0] + (255 - COLOR_SKIN[0]) * strain_factor)
            g = int(COLOR_SKIN[1] - (COLOR_SKIN[1] - 120) * strain_factor)
            b = int(COLOR_SKIN[2] - (COLOR_SKIN[2] - 120) * strain_factor)
            current_skin = (r, g, b)

        # Head Base Circle
        pygame.draw.circle(self.screen, current_skin, (head_cx, head_cy), head_radius)
        pygame.draw.circle(self.screen, (180, 120, 80), (head_cx, head_cy), head_radius, 3)

        # Cute Boy Ears
        pygame.draw.circle(self.screen, current_skin, (head_cx - head_radius + 4, head_cy + 4), 10)
        pygame.draw.circle(self.screen, (180, 120, 80), (head_cx - head_radius + 4, head_cy + 4), 2)

        # --- D. CHEEKS (PUFFED CARTOON BALLOON CHEEKS WHEN BLOWING) ---
        if self.is_blowing and not self.game_won:
            puff_size = 14 + int((self.pressure / 100.0) * 10)
            cheek_color = COLOR_CHEEKS_BLOW
            # Left puffed cheek
            pygame.draw.circle(self.screen, cheek_color, (head_cx - 24, head_cy + 14), puff_size)
            pygame.draw.circle(self.screen, (200, 30, 30), (head_cx - 24, head_cy + 14), puff_size, 2)
            # Right puffed cheek (facing the bag!)
            pygame.draw.circle(self.screen, cheek_color, (head_cx + 26, head_cy + 14), puff_size + 2)
            pygame.draw.circle(self.screen, (200, 30, 30), (head_cx + 26, head_cy + 14), puff_size + 2, 2)
        else:
            # Normal cute blush spots
            pygame.draw.circle(self.screen, COLOR_CHEEKS_NORMAL, (head_cx - 22, head_cy + 14), 8)
            pygame.draw.circle(self.screen, COLOR_CHEEKS_NORMAL, (head_cx + 22, head_cy + 14), 8)

        # --- E. EYES & EXPRESSIONS ---
        eye_y = head_cy - 4
        if self.game_won:
            # Happy smiling closed eyes (^ ^)
            pygame.draw.arc(self.screen, (30, 30, 30), (head_cx - 24, eye_y - 6, 18, 16), 0, math.pi, 3)
            pygame.draw.arc(self.screen, (30, 30, 30), (head_cx + 8, eye_y - 6, 18, 16), 0, math.pi, 3)
        elif self.is_blowing:
            if self.pressure > 75.0:
                # Comically strained wide eyes with tiny pupils!
                pygame.draw.circle(self.screen, (255, 255, 255), (head_cx - 14, eye_y), 9)
                pygame.draw.circle(self.screen, (255, 255, 255), (head_cx + 14, eye_y), 9)
                pygame.draw.circle(self.screen, (40, 40, 40), (head_cx - 14, eye_y), 9, 2)
                pygame.draw.circle(self.screen, (40, 40, 40), (head_cx + 14, eye_y), 9, 2)
                # Tiny pupils vibrating
                pupil_offset = random.uniform(-1, 1)
                pygame.draw.circle(self.screen, (200, 20, 20), (int(head_cx - 14 + pupil_offset), int(eye_y)), 3)
                pygame.draw.circle(self.screen, (200, 20, 20), (int(head_cx + 14 + pupil_offset), int(eye_y)), 3)
            else:
                # Determined squinted blowing eyes (> <)
                pygame.draw.line(self.screen, (30, 30, 30), (head_cx - 22, eye_y - 3), (head_cx - 10, eye_y + 3), 3)
                pygame.draw.line(self.screen, (30, 30, 30), (head_cx - 22, eye_y + 3), (head_cx - 10, eye_y - 3), 3)

                pygame.draw.line(self.screen, (30, 30, 30), (head_cx + 8, eye_y - 3), (head_cx + 20, eye_y + 3), 3)
                pygame.draw.line(self.screen, (30, 30, 30), (head_cx + 8, eye_y + 3), (head_cx + 20, eye_y - 3), 3)
        else:
            # Normal or blinking eyes
            if self.is_blinking:
                pygame.draw.line(self.screen, (30, 30, 30), (head_cx - 22, eye_y), (head_cx - 6, eye_y), 3)
                pygame.draw.line(self.screen, (30, 30, 30), (head_cx + 6, eye_y), (head_cx + 22, eye_y), 3)
            else:
                # Big cute cartoon eyes
                # Left eye
                pygame.draw.circle(self.screen, (255, 255, 255), (head_cx - 14, eye_y), 9)
                pygame.draw.circle(self.screen, (40, 80, 180), (head_cx - 13, eye_y), 6)
                pygame.draw.circle(self.screen, (20, 20, 20), (head_cx - 13, eye_y), 3)
                pygame.draw.circle(self.screen, (255, 255, 255), (head_cx - 15, eye_y - 2), 2)
                # Right eye
                pygame.draw.circle(self.screen, (255, 255, 255), (head_cx + 14, eye_y), 9)
                pygame.draw.circle(self.screen, (40, 80, 180), (head_cx + 15, eye_y), 6)
                pygame.draw.circle(self.screen, (20, 20, 20), (head_cx + 15, eye_y), 3)
                pygame.draw.circle(self.screen, (255, 255, 255), (head_cx + 13, eye_y - 2), 2)

        # Eyebrows
        if self.is_blowing and self.pressure > 60:
            # Furrowed strained eyebrows
            pygame.draw.line(self.screen, (40, 30, 20), (head_cx - 24, eye_y - 12), (head_cx - 8, eye_y - 7), 3)
            pygame.draw.line(self.screen, (40, 30, 20), (head_cx + 8, eye_y - 7), (head_cx + 24, eye_y - 12), 3)
        else:
            # Friendly curved eyebrows
            pygame.draw.arc(self.screen, (40, 30, 20), (head_cx - 24, eye_y - 18, 16, 12), 0.2, math.pi * 0.9, 3)
            pygame.draw.arc(self.screen, (40, 30, 20), (head_cx + 8, eye_y - 18, 16, 12), 0.1, math.pi * 0.8, 3)

        # --- F. MOUTH ---
        mouth_y = head_cy + 22
        if self.game_won:
            # Huge triumphant open smile!
            mouth_rect = pygame.Rect(head_cx - 18, mouth_y - 4, 36, 22)
            pygame.draw.arc(self.screen, (160, 20, 20), mouth_rect, math.pi, 2 * math.pi, 14)
            # White teeth
            pygame.draw.rect(self.screen, (255, 255, 255), (head_cx - 12, mouth_y + 1, 24, 5), border_radius=2)
        elif self.is_blowing:
            # Puckered trumpet lips blowing directly toward the bag
            pygame.draw.ellipse(self.screen, (220, 70, 70), (head_cx + 28, mouth_y - 8, 18, 14))
            pygame.draw.ellipse(self.screen, (120, 20, 20), (head_cx + 34, mouth_y - 5, 8, 8))
        else:
            # Small resting smile
            pygame.draw.arc(self.screen, (80, 40, 30), (head_cx - 10, mouth_y - 6, 20, 14), math.pi * 1.1, math.pi * 1.9, 3)

        # --- G. MESSY CARTOON HAIR ---
        hair_pts = [
            (head_cx - 44, head_cy - 10),
            (head_cx - 46, head_cy - 35),
            (head_cx - 30, head_cy - 48),
            (head_cx - 18, head_cy - 56),  # Hair tuft 1
            (head_cx - 10, head_cy - 48),
            (head_cx + 4, head_cy - 58),   # Hair tuft 2 (wiggles!)
            (head_cx + 16, head_cy - 48),
            (head_cx + 36, head_cy - 44),
            (head_cx + 46, head_cy - 20),
            (head_cx + 42, head_cy - 2),
            (head_cx + 30, head_cy - 20),
            (head_cx + 10, head_cy - 24),
            (head_cx - 10, head_cy - 22),
            (head_cx - 32, head_cy - 18)
        ]
        pygame.draw.polygon(self.screen, COLOR_HAIR, hair_pts)
        pygame.draw.polygon(self.screen, (30, 20, 15), hair_pts, 2)

    # -----------------------------------------------------------------------
    # DRAWING ROUTINES: THE EXPANDING POLYTHENE BAG
    # -----------------------------------------------------------------------
    def draw_polythene_bag(self):
        """Draws the translucent, cartoon plastic bag that dynamically expands and wobbles."""
        if self.game_won:
            return  # Bag has bursted!

        # Origin point at schoolboy's mouth / hands
        origin_x = 328
        origin_y = 330

        # Calculate dynamic size based on pressure (0 to 100%)
        # Normal uninflated bag: ~30px radius. Max: ~160px radius!
        progress = self.pressure / 100.0
        bag_radius_x = int(32 + progress * 135)
        bag_radius_y = int(28 + progress * 115)

        # High pressure wobble deformation (sinusoidal vibration)
        wobble_freq = 0.35 + progress * 0.45
        wobble_amp = progress * (6.0 if self.pressure < 70 else 14.0)
        wobble_x = math.sin(self.anim_tick * wobble_freq) * wobble_amp
        wobble_y = math.cos(self.anim_tick * wobble_freq * 1.3) * wobble_amp

        # Center of the expanding bag moves forward as it grows
        bag_center_x = origin_x + bag_radius_x * 0.95 + wobble_x
        bag_center_y = origin_y - bag_radius_y * 0.15 + wobble_y

        # Transparent surface for authentic translucent plastic appearance
        surf_w = int(bag_radius_x * 2 + 50)
        surf_h = int(bag_radius_y * 2 + 50)
        bag_surface = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        local_cx = surf_w // 2
        local_cy = surf_h // 2

        # 1. Bag Body (Translucent gradient layers)
        # As it expands, plastic stretches thinner (alpha decreases slightly, color gets brighter)
        alpha_base = int(175 - progress * 45)
        base_color = (
            int(COLOR_BAG_TINT[0] + progress * 35),
            int(COLOR_BAG_TINT[1] + progress * 25),
            255,
            alpha_base
        )
        pygame.draw.ellipse(bag_surface, base_color, 
                            (local_cx - bag_radius_x, local_cy - bag_radius_y, bag_radius_x * 2, bag_radius_y * 2))

        # 2. Polythene Crinkles & Crease Lines
        crease_color = (255, 255, 255, int(160 - progress * 50))
        # Top crease
        pygame.draw.arc(bag_surface, crease_color, 
                        (local_cx - bag_radius_x * 0.8, local_cy - bag_radius_y * 0.7, bag_radius_x * 1.6, bag_radius_y * 1.2), 
                        0.5, 2.5, 2)
        # Bottom crease
        pygame.draw.arc(bag_surface, crease_color, 
                        (local_cx - bag_radius_x * 0.6, local_cy - bag_radius_y * 0.4, bag_radius_x * 1.2, bag_radius_y * 1.1), 
                        3.6, 5.8, 2)

        # 3. Glossy Plastic Highlights (Shininess)
        # Long curved highlight streak on the top-left of the bag
        hl_rect = pygame.Rect(local_cx - bag_radius_x * 0.82, local_cy - bag_radius_y * 0.78, 
                              int(bag_radius_x * 0.9), int(bag_radius_y * 0.55))
        pygame.draw.arc(bag_surface, (255, 255, 255, 220), hl_rect, 1.2, 2.8, 4)
        # Secondary small gloss spot
        pygame.draw.ellipse(bag_surface, (255, 255, 255, 190), 
                            (local_cx - bag_radius_x * 0.6, local_cy - bag_radius_y * 0.65, 16 + progress * 10, 8 + progress * 4))

        # 4. Bag Perimeter Outline
        outline_alpha = int(210 - progress * 40)
        outline_color = (COLOR_BAG_OUTLINE[0], COLOR_BAG_OUTLINE[1], COLOR_BAG_OUTLINE[2], outline_alpha)
        pygame.draw.ellipse(bag_surface, outline_color, 
                            (local_cx - bag_radius_x, local_cy - bag_radius_y, bag_radius_x * 2, bag_radius_y * 2), 3)

        # Blit the transparent bag to screen
        self.screen.blit(bag_surface, (bag_center_x - local_cx, bag_center_y - local_cy))

        # 5. Bag Neck & Tied Handles attached to mouth
        neck_pts = [
            (origin_x - 12, origin_y - 8),
            (int(bag_center_x - bag_radius_x * 0.82), int(bag_center_y - 12)),
            (int(bag_center_x - bag_radius_x * 0.82), int(bag_center_y + 16)),
            (origin_x - 12, origin_y + 12)
        ]
        neck_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(neck_surf, (120, 220, 255, 190), neck_pts)
        pygame.draw.polygon(neck_surf, (50, 160, 220, 220), neck_pts, 2)
        self.screen.blit(neck_surf, (0, 0))

    # -----------------------------------------------------------------------
    # DRAWING ROUTINES: HUD, GAUGES, BUTTONS & POP EFFECT
    # -----------------------------------------------------------------------
    def draw_hud(self):
        # 1. Top Pressure Gauge Container
        bar_w = 380
        bar_h = 32
        bar_x = (SCREEN_WIDTH - bar_w) // 2
        bar_y = 18

        # Background Bar
        pygame.draw.rect(self.screen, (240, 240, 245), (bar_x - 6, bar_y - 6, bar_w + 12, bar_h + 12), border_radius=12)
        pygame.draw.rect(self.screen, COLOR_WOOD_DARK, (bar_x - 6, bar_y - 6, bar_w + 12, bar_h + 12), 3, border_radius=12)
        pygame.draw.rect(self.screen, (210, 215, 225), (bar_x, bar_y, bar_w, bar_h), border_radius=8)

        # Color Gradient Calculation for Pressure Fill:
        # Green (0-50%) -> Amber Yellow (50-75%) -> Fiery Crimson Red (75-100%)
        if self.pressure < 50.0:
            fill_color = (46, 204, 113)  # Bright Green
        elif self.pressure < 78.0:
            fill_color = (241, 196, 15)  # Alert Yellow
        else:
            # Flashing red at dangerous high pressure!
            flash = (self.anim_tick % 10 < 5)
            fill_color = (231, 76, 60) if flash else (255, 50, 50)

        fill_w = int((self.pressure / 100.0) * bar_w)
        if fill_w > 0:
            pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill_w, bar_h), border_radius=8)
            # Shine reflection on top of bar
            pygame.draw.line(self.screen, (255, 255, 255, 180), (bar_x + 4, bar_y + 4), (bar_x + fill_w - 4, bar_y + 4), 2)

        # Percentage text
        txt_percent = self.font_body.render(f"PRESSURE: {int(self.pressure)}%", True, (40, 40, 40))
        self.screen.blit(txt_percent, (bar_x + (bar_w - txt_percent.get_width()) // 2, bar_y + 4))

        # Warning text when reaching burst limit
        if self.pressure > 80.0 and not self.game_won:
            txt_warn = self.font_body.render("⚠️ DANGER! READY TO POP! ⚠️", True, (220, 20, 20))
            self.screen.blit(txt_warn, ((SCREEN_WIDTH - txt_warn.get_width()) // 2, bar_y + 42))

        # 2. Control Prompt at Bottom
        if not self.game_won:
            bounce = math.sin(self.anim_tick * 0.15) * 4.0
            prompt_bg = pygame.Rect(SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT - 65 + int(bounce), 420, 44)
            pygame.draw.rect(self.screen, (255, 255, 255), prompt_bg, border_radius=22)
            pygame.draw.rect(self.screen, COLOR_SHIRT, prompt_bg, 3, border_radius=22)

            key_text = "💨 HOLD [SPACEBAR] TO BLOW!" if not self.is_blowing else "💨 BLOWING HARD!! KEEP GOING!"
            txt_prompt = self.font_body.render(key_text, True, COLOR_SHIRT if not self.is_blowing else (220, 20, 20))
            self.screen.blit(txt_prompt, (prompt_bg.centerx - txt_prompt.get_width() // 2, prompt_bg.centery - txt_prompt.get_height() // 2))

        # 3. Audio & Controls Legend (Top Left)
        sound_status = "MUTED" if self.sound_muted else "ON"
        legend_txt = self.font_small.render(f"[M] Sound: {sound_status}   |   [R] Restart", True, (90, 90, 100))
        self.screen.blit(legend_txt, (14, SCREEN_HEIGHT - 26))

    # -----------------------------------------------------------------------
    # DRAWING ROUTINES: BURST & VICTORY POPUP
    # -----------------------------------------------------------------------
    def draw_burst_and_victory(self):
        """Draws the comic-style POP starburst explosion and victory celebratory screen."""
        if not self.game_won:
            return

        # 1. Comic POP Starburst Animation (First 35 frames)
        if self.burst_timer < 35:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_alpha = max(0, int(200 * (1.0 - self.burst_timer / 35.0)))
            flash_surf.fill((255, 255, 240, flash_alpha))
            self.screen.blit(flash_surf, (0, 0))

            # Jagged Comic Explosion Star
            center_x = 510
            center_y = 330
            star_radius = min(220, self.burst_timer * 12 + 40)
            star_pts = []
            num_points = 18
            for i in range(num_points):
                ang = (i / num_points) * 2 * math.pi
                r = star_radius if (i % 2 == 0) else star_radius * 0.52
                star_pts.append((center_x + math.cos(ang) * r, center_y + math.sin(ang) * r))

            pygame.draw.polygon(self.screen, (255, 220, 0), star_pts)
            pygame.draw.polygon(self.screen, (255, 80, 0), star_pts, 5)

            # Comic "POP!!" Text
            txt_pop = self.font_pop.render("POP!!", True, (255, 30, 30))
            txt_pop_shadow = self.font_pop.render("POP!!", True, (40, 20, 20))
            self.screen.blit(txt_pop_shadow, (center_x - txt_pop.get_width() // 2 + 5, center_y - txt_pop.get_height() // 2 + 5))
            self.screen.blit(txt_pop, (center_x - txt_pop.get_width() // 2, center_y - txt_pop.get_height() // 2))

        # 2. Victory Modal Banner (Appears smoothly after pop)
        if self.burst_timer >= 18:
            # Confetti raining down
            for conf in self.confetti_list:
                conf.draw(self.screen)

            # Semi-transparent dark overlay behind modal
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 75))
            self.screen.blit(overlay, (0, 0))

            # Modal Banner Card
            modal_w = 520
            modal_h = 320
            modal_rect = pygame.Rect((SCREEN_WIDTH - modal_w) // 2, (SCREEN_HEIGHT - modal_h) // 2 - 20, modal_w, modal_h)

            pygame.draw.rect(self.screen, (255, 255, 255), modal_rect, border_radius=20)
            pygame.draw.rect(self.screen, (255, 215, 0), modal_rect, 6, border_radius=20)  # Gold trim
            pygame.draw.rect(self.screen, (40, 40, 40), modal_rect, 2, border_radius=20)

            # Golden Ribbon Header
            ribbon_rect = pygame.Rect(modal_rect.x + 30, modal_rect.y - 24, modal_w - 60, 56)
            pygame.draw.rect(self.screen, (255, 80, 50), ribbon_rect, border_radius=14)
            pygame.draw.rect(self.screen, (255, 215, 0), ribbon_rect, 3, border_radius=14)

            txt_win = self.font_title.render("🎉 YOU WIN! 🎉", True, (255, 255, 255))
            self.screen.blit(txt_win, (ribbon_rect.centerx - txt_win.get_width() // 2, ribbon_rect.centery - txt_win.get_height() // 2))

            # Subtitles & Funny Stats
            txt_congrats = self.font_header.render("BAG BURSTED SUCCESSFULLY!", True, (46, 125, 50))
            txt_flavor = self.font_body.render("The loud pop echoed across the classroom!", True, (70, 70, 80))
            txt_stat = self.font_body.render(f"⏱️ Burst Time: {self.total_time:.1f}s   |   💥 Pressure: 100%", True, COLOR_SHIRT)

            self.screen.blit(txt_congrats, (modal_rect.centerx - txt_congrats.get_width() // 2, modal_rect.y + 54))
            self.screen.blit(txt_flavor, (modal_rect.centerx - txt_flavor.get_width() // 2, modal_rect.y + 98))
            self.screen.blit(txt_stat, (modal_rect.centerx - txt_stat.get_width() // 2, modal_rect.y + 134))

            # Interactive Restart Button
            btn_color = (46, 204, 113) if not self.btn_hover else (39, 174, 96)
            self.btn_restart_rect.x = modal_rect.centerx - self.btn_restart_rect.w // 2
            self.btn_restart_rect.y = modal_rect.bottom - 74

            pygame.draw.rect(self.screen, btn_color, self.btn_restart_rect, border_radius=16)
            pygame.draw.rect(self.screen, (255, 255, 255), self.btn_restart_rect, 3, border_radius=16)

            txt_btn = self.font_body.render("PLAY AGAIN (Press R)", True, (255, 255, 255))
            self.screen.blit(txt_btn, (self.btn_restart_rect.centerx - txt_btn.get_width() // 2, 
                                       self.btn_restart_rect.centery - txt_btn.get_height() // 2))

    # -----------------------------------------------------------------------
    # MAIN LOOP
    # -----------------------------------------------------------------------
    def run(self):
        while self.running:
            self.handle_events()
            self.update()

            # 1. Draw Classroom
            self.draw_classroom_background()
            self.draw_school_desk()

            # 2. Draw Characters & Animated Objects
            self.draw_schoolboy()
            self.draw_polythene_bag()

            # 3. Draw Active Particles
            for p in self.air_particles:
                p.draw(self.screen)
            for s in self.sweat_particles:
                s.draw(self.screen)
            for shred in self.plastic_shreds:
                shred.draw(self.screen)

            # 4. Draw HUD / Gauges
            self.draw_hud()

            # 5. Draw Victory Screen & Explosions
            self.draw_burst_and_victory()

            # Refresh display at steady 60 FPS
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    game = PlasticBagBusterGame()
    game.run()

