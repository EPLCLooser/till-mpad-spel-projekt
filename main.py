import serial.tools.list_ports
import time
import pygame
import sys
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SHOOT_COOLDOWN = 0.5
BULLET_SPEED = 15
ENEMY_SPEED = 60

# Variables
enemy_spawn_interval = 5
text_timer = 0

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Star Blaster")
background = pygame.image.load("background_img.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Initialize the mixer for sounds
pygame.mixer.init()
pygame.mixer.music.load("Background_music.mp3")
pygame.mixer.music.play(-1)
gameoversound = pygame.mixer.Sound('gameover_sound.mp3')
shootingsound = pygame.mixer.Sound('shooting_sound.mp3')


# game over function
def gameOver():
    global kill_count
    global running
    game_over = Text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, "Impact", 90, "Game Over", (255, 0, 0))
    highscore()
    all_sprites.add(game_over)
    pygame.mixer.Sound.play(gameoversound)
    pygame.mixer.music.stop()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                running = False

        # Draw the background and all sprites
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        pygame.display.update()
    return

def highscore():
    global kill_count
    highscore = open("high_score.txt")
    highscore_value = int(highscore.read())
    highscore.close()
    if highscore_value < kill_count:
        highscore = open("high_score.txt", "w")
        print(kill_count)
        highscore.write(str(kill_count))
        highscore = Text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 90, "Impact", 60, "New High Score: {}".format(kill_count), (255, 0, 0))
    else:
        highscore = Text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 90, "Impact", 90, "High Score: {}".format(highscore_value), (255, 0, 0))
    all_sprites.add(highscore)

def exit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            running = False


# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("pixel-art-rocket.png") 
        self.image = pygame.transform.scale(self.image, (80, 100))  # Scale the image to a smaller size
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def updatePlayer(self, input):
        global shot_time
        try:
            if input[0] >= 10:
                self.rect.x -= int((input[0] - 10) * (4 - 1) / (45 - 10) + 1)
            elif input[0] <= -10:
                self.rect.x += int((abs(input[0]) - 10) * (4 - 1) / (45 - 10) + 1)
            if input[1] <= -10:
                self.rect.y -= int((abs(input[1]) - 10) * (4 - 1) / (45 - 10) + 1)
            elif input[1] >= 10:
                self.rect.y += int((input[1] - 10) * (4 - 1) / (45 - 10) + 1)

            # Shooting
            if input[2] == 1 and time.time() - shot_time >= SHOOT_COOLDOWN:
                    shot_time = time.time()
                    pygame.mixer.Sound.play(shootingsound)
                    bullet = Bullet(self)
                    all_sprites.add(bullet)

        except IndexError:
            pass

        # Keep the player within screen boundaries
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Check for collision with enemies
        if pygame.sprite.spritecollideany(self, enemies): 
            self.kill()
            gameOver()   

class Bullet(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = pygame.Surface((10, 20))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.centerx = player.rect.centerx
        self.rect.top = player.rect.top

    def update(self):
        self.rect.y -= BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.image.load("monster.png")
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.topright = (x, 0)

    def update(self, move=False):
        if move:
            self.rect.y += ENEMY_SPEED
            if self.rect.bottom >= SCREEN_HEIGHT:
                gameOver()

class Text(pygame.sprite.Sprite):
    def __init__(self, x, y, font, font_size, text, color):
        super().__init__()
        self.font = pygame.font.SysFont(font, font_size)
        self.image = self.font.render(text, True, color) 
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, input=None):
        if input == "kill":
            self.kill()
        elif input == "update":
            self.image = self.font.render(str(kill_count), True, (255, 255, 255)) 
            self.rect.topleft = (30, 30)

# Create a sprite group for all enemies
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

# Set up serial communication
ports = serial.tools.list_ports.comports()
ser = serial.Serial()

# set communication settings
ser.baudrate = 9600
ser.port = "COM4"

# Check if the port is available and open it
try:
    ser.close()
    ser.open()
except Exception as e:
    print(f"Error opening serial port: {e}")
    sys.exit()

# Start screen
start = False
running = True
game_header = Text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, "Impact", 90, "Star Blaster", (255, 255, 255))
press_start = Text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 90, "Impact", 30, "Press The Button on Your Controller to Start", (255, 255, 255))
all_sprites.add(game_header, press_start)
dir_up = True
distance_of_text = 10
counter = 0

while not start:

    # Takes event and breaks the while loop
    exit()

    # Check for controller input
    if ser.in_waiting:
        inoInput = ser.readline().decode('utf-8', errors='ignore').strip()
        try:
            inputArr = list(map(int, inoInput.split(" ")))
            if len(inputArr) == 3 and inputArr[2] == 1:
                start = True
        except ValueError:
            print(f"Invalid input: {inoInput}")
            inputArr = [0, 0, 0]

    # Draw the start screen
    screen.blit(background, (0, 0))

    # Draw all sprites
    all_sprites.draw(screen)

    # Update the display
    pygame.display.update()

game_header.update("kill")
press_start.update("kill")

# add the player
player = Player(SCREEN_WIDTH/2, SCREEN_HEIGHT)
all_sprites.add(player)

# initialize time global variables
shot_time = time.time() + 2 # to avoid the first shot immediately
enemy_spawn_time = time.time() + 1 # to avoid the first enemy spawn immediately
difficulty = Text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 90, "Impact", 40, "Difficulty Increased", (255, 0, 0))
kill_count = 0
kill_count_text = Text(30, 30, "Impact", 20, str(kill_count), (255, 255, 255))
all_sprites.add(kill_count_text)

# Game loop
while running:
    # Takes keyboard input and breaks the while loop if escape is pressed
    exit()

    if ser.in_waiting:
        inoInput = ser.readline().decode('utf-8', errors='ignore').strip()
        try:
            inputArr = list(map(int, inoInput.split(" ")))
        except ValueError:
            print(f"Invalid input: {inoInput}")
            inputArr = [0, 0, 0]
        player.updatePlayer(inputArr)

    # spawns random amount of enemies
    if time.time() - enemy_spawn_time >= enemy_spawn_interval:
        enemies.update(True)
        enemy_spawn_time = time.time()
        amount_of_enemies = random.randint(1, 10)
        random_numbers = random.sample(range(1, 11), amount_of_enemies)
        for n in range(amount_of_enemies):
            x = random_numbers[n] * 80
            if x > SCREEN_WIDTH:
                x = SCREEN_WIDTH - 80
            enemies.add(Enemy(x))

    # Check for collisions between bullets and enemies
    for bullet in all_sprites:
        if isinstance(bullet, Bullet):
            if pygame.sprite.spritecollide(bullet, enemies, True):
                bullet.kill()  # Remove the bullet
                kill_count += 1
                kill_count_text.update("update")

                # increase the spawn rate of enemies
                if kill_count % 5 == 0 and enemy_spawn_interval > 2:
                    enemy_spawn_interval -= 0.5
                    all_sprites.add(difficulty)
                    text_timer = time.time()

    if time.time() - text_timer >= 1:
        difficulty.update("kill")

    # Update and draw everything
    all_sprites.update()
    enemies.update()

    # Draw the background
    screen.blit(background, (0, 0))

    # Draw all sprites
    enemies.draw(screen)
    all_sprites.draw(screen)

    # Update the display
    pygame.display.update()


# Quit Pygame
pygame.quit()
sys.exit()