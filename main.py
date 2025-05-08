# File: main.py
# Author: Lucas Norrflod
# Date: 8/5-2025
# Description: This is a 2d game where you control the player with an array that comes from the serial port. The game is about you trying to kill aliens coming down the screen and you shoot them in order to get a high score. The game include waves and a way to save your highscore

# import libraries
import serial.tools.list_ports
import time
import pygame
import sys
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BULLET_SPEED = 15
ENEMY_SPEED = 60

# Variables
enemy_spawn_interval = 5
wave_text_timer = 0
shoot_cooldown = 0.5

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

# Creates a wave pattern that enemies will spawn in and decreases the interval for enemy spawn time
# Parameters: wave_num: integer that decides the wave number
# Returns the wave pattern as a 2d array
def wave(wave_num):
    global enemy_spawn_interval
    if enemy_spawn_interval > 2:
        enemy_spawn_interval -= 0.5
    
    if wave_num > 6:
        wave_num = random.randrange(2, 6)
    
    if wave_num == 1:
        pattern = [[2, 5, 6, 9], [2, 3, 8, 9], [1, 4, 7, 10]] #The inner array are the positions that the enemies will spawn in
    elif wave_num == 2:
        pattern = [[1, 3, 5, 7, 9], [2, 4, 6, 8, 10], [1, 3, 5, 7, 9], [2, 4, 6, 8, 10]]
    elif wave_num == 3:
        pattern = [[5, 6], [4, 5, 6, 7], [3, 4, 5, 6, 7, 8], [2, 3, 4, 5, 6, 7, 8, 9], [2, 3, 4, 5, 6, 7, 8, 9], [3, 4, 7, 8]]
    elif wave_num == 4:
        pattern = [[1, 2, 5, 6, 9, 10], [1, 2, 3, 4, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8], [3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 4, 5, 6, 7, 9, 10]]
    elif wave_num == 5:
        pattern = [[3, 8], [2, 3, 4, 7, 8, 9], [2, 3, 4, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [3, 4, 5, 6, 7, 8], [4, 5, 6, 7], [5, 6], [5], [6]]
    else:
        pattern = [[2, 4, 6, 8, 10], [2, 8], [2, 4, 6, 8, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [2, 9]]
    return pattern


# When player lose this function runs the game-over-screen and shows the high score
def gameOver():
    global kill_count
    global running
    game_over = Text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, "Impact", 90, "Game Over", (255, 0, 0))
    highscore()
    all_sprites.add(game_over)
    pygame.mixer.Sound.play(gameoversound)
    pygame.mixer.music.stop()
    while running:
        exit()

        # Draw the background and all sprites
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        pygame.display.update()
    return

# Takes the global kill_count variable and changes the highscore text-file if it is higher
def highscore():
    global kill_count
    highscore = open("high_score.txt")
    highscore_value = int(highscore.read())
    highscore.close()
    if highscore_value < kill_count:
        highscore = open("high_score.txt", "w")
        highscore.write(str(kill_count))
        highscore = Text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 90, "Impact", 60, "New High Score: {}".format(kill_count), (255, 0, 0))
    else:
        highscore = Text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 90, "Impact", 90, "High Score: {}".format(highscore_value), (255, 0, 0))
    all_sprites.add(highscore)

# Checks if escape key is pressed and closes the program if that is true
def exit():
    global running
    global start
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            start = True
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            running = False
            start = True

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("pixel-art-rocket.png") 
        self.image = pygame.transform.scale(self.image, (80, 100))  # Scale the image to a smaller size
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    # moves the player depending on input
    # parameter: input: array of y and x tilt-angle
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

            # Checks if shooting cooldown is done and shows the player that it is ready. Then it checks if the button is pressed and then spawns in the bullet objekt
            if time.time() - shot_time >= shoot_cooldown:
                all_sprites.add(laser_ready_text)
                laser_ready_text.update() 
                if input[2] == 1:
                    shot_time = time.time()
                    pygame.mixer.Sound.play(shootingsound)
                    bullet = Bullet(self)
                    all_sprites.add(bullet)
            else:
                laser_ready_text.update("kill")
        except IndexError:
            pass
            print("Invalid input array length: {}".format(len(input)))

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

    # Moves the bullet upwards and when it is of screen it self kills
    def update(self):
        self.rect.y -= BULLET_SPEED
        if self.rect.bottom < 0:
            global shoot_cooldown
            global kill_streak
            kill_streak = 0
            kill_streak_text.update("update", "STREAK: {}".format(kill_streak))
            shoot_cooldown = 0.5
            self.kill()

class Enemy(pygame.sprite.Sprite):
    amount_of_enemies = 0

    def __init__(self, x):
        Enemy.amount_of_enemies += 1
        super().__init__()
        self.image = pygame.image.load("monster.png")
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.topright = (x, 0)

    # Moves the enemy down if move is true and runs the gameOver function if an enemy reaches the bottom.
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

    # Parameters: 
    # update_status: string either kill, update or None
    #
    def update(self, update_status=None, input=None):
        if update_status == "kill":
            self.kill()
        elif update_status == "update":
            self.image = self.font.render(str(input), True, (255, 255, 255)) 

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

while not start:
    # Takes event and breaks the while loop
    exit()
    start = not running

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

# initialize game loop variables and timers
shot_time = time.time() + 2 # to avoid the first shot immediately
enemy_spawn_time = time.time() + 1 # to avoid the first enemy spawn immediately
kill_count = 0
kill_streak = 0
kill_count_text = Text(30, 30, "Impact", 20, str(kill_count), (255, 255, 255))
kill_streak_text = Text(SCREEN_WIDTH - 60, 30, "Impact", 20, "STREAK: {}".format(kill_streak), (255, 255, 255))
all_sprites.add(kill_count_text)
all_sprites.add(kill_streak_text)
laser_ready_text = Text(70, SCREEN_HEIGHT - 30, "Impact", 20, "LASER READY", (255, 255, 255))
row = 0
wave_counter = 1
wave_text = Text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 90, "Impact", 40, "Wave {}".format(wave_counter), (255, 0, 0))
all_sprites.add(wave_text)
wave_text_timer = time.time()
pause = False


# Game loop
while running:
    # Takes keyboard input and breaks the while loop if escape is pressed
    exit()

    # Reads the serialport
    if ser.in_waiting:
        inoInput = ser.readline().decode('utf-8', errors='ignore').strip() #Decode the serial port input
        try:
            inputArr = list(map(int, inoInput.split(" "))) #makes inoInput into an array
        except ValueError:
            print(f"Invalid input: {inoInput}")
            inputArr = [0, 0, 0]
        player.updatePlayer(inputArr)

    # spawn enemies
    if time.time() - enemy_spawn_time >= enemy_spawn_interval:
        enemies.update(True)
        enemy_layout = wave(wave_counter)
        enemy_spawn_time = time.time()
        if not pause:
            for n in range(len(enemy_layout[row])):
                x = enemy_layout[row][n] * 80 # Spawns the enemy of the position that it is assigned
                enemies.add(Enemy(x)) #adds Enemy to the enemy group
        if row >= len(enemy_layout) - 1:
            pause = True
            if Enemy.amount_of_enemies == 0: #Waits for all enemies to be killed before the next wave
                pause = False
                row = 0
                wave_counter += 1
                wave_text = Text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 90, "Impact", 40, "Wave {}".format(wave_counter), (255, 0, 0))
                all_sprites.add(wave_text)
                wave_text_timer = time.time()
        else:
            row += 1

    # Check for collisions between bullets and enemies and adds points to score and streak
    for bullet in all_sprites:
        if isinstance(bullet, Bullet):
            if pygame.sprite.spritecollide(bullet, enemies, True):
                Enemy.amount_of_enemies -= 1
                bullet.kill()  # Remove the bullet
                kill_count += 1
                kill_streak += 1
                shoot_cooldown *= 0.99 #decreases the shoot cooldown by one percent
                kill_count_text.update("update", str(kill_count))
                kill_streak_text.update("update", "STREAK: {}".format(kill_streak))

    if time.time() - wave_text_timer >= 1:
        wave_text.update("kill")

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