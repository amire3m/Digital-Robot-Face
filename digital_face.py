import pygame
import numpy as np
import sounddevice as sd
import threading
import random
import math
import time

# تنظیمات پنجره
WIDTH, HEIGHT = 500, 500
CENTER = (WIDTH // 2, HEIGHT // 2)

# رنگ‌ها
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_BLUE = (150, 200, 255)
RED = (255, 60, 60)
YELLOW = (255, 255, 150)

# حالت‌های چهره رباتی
FACE_MODES = {
    "neutral": {"face_color": GRAY, "eye_color": LIGHT_BLUE, "mouth_color": BLACK},
    "happy": {"face_color": (180, 220, 255), "eye_color": YELLOW, "mouth_color": BLACK},
    "angry": {"face_color": (150, 0, 0), "eye_color": RED, "mouth_color": RED},
    "sad": {"face_color": (60, 60, 120), "eye_color": LIGHT_BLUE, "mouth_color": BLACK},
    "polite": {"face_color": (100, 150, 180), "eye_color": LIGHT_BLUE, "mouth_color": BLACK},
}

volume_level = 0.0

def audio_callback(indata, frames, time, status):
    global volume_level
    volume_level = np.linalg.norm(indata)

def start_audio_stream():
    stream = sd.InputStream(callback=audio_callback)
    stream.start()

class RobotFace:
    def __init__(self, screen):
        self.screen = screen
        self.mouth_opening = 0
        self.eye_direction = [0, 0]
        self.last_eye_move = time.time()
        self.head_offset = [0, 0]
        self.blink_timer = time.time()
        self.blinking = False
        self.face_mode = "neutral"
        self.blink_state = 0

    def update(self):
        global volume_level
        v = min(volume_level, 0.15)
        self.mouth_opening = int((v / 0.15) * 35)

        # حرکت چشم‌ها هر 1.5 تا 3 ثانیه
        if time.time() - self.last_eye_move > random.uniform(1.5, 3.0):
            self.eye_direction = [random.randint(-5, 5), random.randint(-3, 3)]
            self.last_eye_move = time.time()

        # لرزش سر سینوسی
        t = time.time()
        self.head_offset[0] = int(math.sin(t * 3) * 4)
        self.head_offset[1] = int(math.cos(t * 2) * 3)

        # چشمک زدن با حالت رباتی: چشم کم کم تیره می‌شود و دوباره باز
        if not self.blinking and time.time() - self.blink_timer > random.uniform(4, 7):
            self.blinking = True
            self.blink_timer = time.time()
            self.blink_state = 0

        if self.blinking:
            self.blink_state += 1
            if self.blink_state > 10:
                self.blinking = False

    def draw(self):
        mode = FACE_MODES[self.face_mode]
        face_color = mode["face_color"]
        eye_color = mode["eye_color"]
        mouth_color = mode["mouth_color"]

        ox, oy = self.head_offset
        cx, cy = CENTER[0] + ox, CENTER[1] + oy

        # صورت رباتی (مستطیل با گوشه‌های گرد)
        pygame.draw.rect(self.screen, face_color, (cx - 120, cy - 130, 240, 260), border_radius=30)
        pygame.draw.rect(self.screen, DARK_GRAY, (cx - 130, cy - 140, 260, 280), width=6, border_radius=35)

        # چشم چپ و راست
        for ex in [-50, 50]:
            eye_x = cx + ex
            eye_y = cy - 40

            # سفیدی چشم رباتی (بیضی)
            pygame.draw.ellipse(self.screen, WHITE, (eye_x - 25, eye_y - 18, 50, 36))

            # چشمک زدن: کم‌کم رنگ مردمک تیره شود
            if self.blinking:
                alpha = max(0, 255 - self.blink_state * 25)
                pupil_color = (*eye_color[:3], alpha)
                # برای پشتیبانی از alpha باید surface جدا بکشیم
                pupil_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.circle(pupil_surface, pupil_color, (15, 15), 12)
                self.screen.blit(pupil_surface, (eye_x - 15 + self.eye_direction[0], eye_y - 15 + self.eye_direction[1]))
            else:
                # مردمک اصلی - دایره بزرگ
                pygame.draw.circle(self.screen, eye_color, (eye_x + self.eye_direction[0], eye_y + self.eye_direction[1]), 12)
                # مردمک کوچک درون آن (یک دایره کوچکتر سفید برای درخشش)
                pygame.draw.circle(self.screen, WHITE, (eye_x + 5 + self.eye_direction[0], eye_y - 5 + self.eye_direction[1]), 5)

        # دهان رباتی - مستطیل با لبه‌های نرم شده
        mouth_w = 80
        mouth_h = max(5, self.mouth_opening)
        mouth_x = cx - mouth_w // 2
        mouth_y = cy + 60
        pygame.draw.rect(self.screen, mouth_color, (mouth_x, mouth_y, mouth_w, mouth_h), border_radius=10)
        pygame.draw.rect(self.screen, DARK_GRAY, (mouth_x - 2, mouth_y - 2, mouth_w + 4, mouth_h + 4), 2, border_radius=12)

def main():
    global face_mode

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🤖 Digital Robot Face")
    clock = pygame.time.Clock()
    face = RobotFace(screen)

    threading.Thread(target=start_audio_stream, daemon=True).start()

    running = True
    print("🎮 کلیدها: 1=خنثی  2=شاد  3=عصبانی  4=ناراحت  5=مودب  ESC=خروج")

    while running:
        screen.fill(BLACK)
        face.update()
        face.draw()
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    face.face_mode = "neutral"
                elif event.key == pygame.K_2:
                    face.face_mode = "happy"
                elif event.key == pygame.K_3:
                    face.face_mode = "angry"
                elif event.key == pygame.K_4:
                    face.face_mode = "sad"
                elif event.key == pygame.K_5:
                    face.face_mode = "polite"

    pygame.quit()

if __name__ == "__main__":
    main()
