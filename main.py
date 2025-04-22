import serial.tools.list_ports
import time
import pygame
import sys

# global variables

# Initialize Pygame
pygame.init()

# Set up the game window
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Star blaster")

# Load the background image
background = pygame.image.load("background_img.png")
background = pygame.transform.scale(background, (screen_width, screen_height))

# game over function

def gameOver():
    global running
    game_over = Text(screen_width/2, screen_height/2, "Impact", 90, "Game Over", (255, 0, 0))
    all_sprites.add(game_over)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                running = False

        # Draw the background
        screen.blit(background, (0, 0))

        # Draw all sprites
        all_sprites.draw(screen)

        # Update the display
        pygame.display.update()

# Define the Player sprite class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        global screen_height, screen_width
        super().__init__()
        self.image = pygame.image.load("pixel-art-rocket.png") 
        self.image = pygame.transform.scale(self.image, (80, 100))  # Scale the image to a smaller size
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def updatePlayer(self, input):
        global shot_time
        shoot_cooldown = 0.5
        try:
            if input[0] >= 10:
                self.rect.x -= int((input[0] - 10) * (4 - 1) / (45 - 10) + 1)
            elif input[0] <= -10:
                self.rect.x += int((abs(input[0]) - 10) * (4 - 1) / (45 - 10) + 1)
            if input[1] <= -10:
                self.rect.y -= int((abs(input[1]) - 10) * (4 - 1) / (45 - 10) + 1)
            elif input[1] >= 10:
                self.rect.y += int((input[1] - 10) * (4 - 1) / (45 - 10) + 1)
            if input[2] == 1:
                if time.time() - shot_time >= shoot_cooldown:
                    print(time.time())
                    shot_time = time.time()
                    bullet = Bullet(self)
                    all_sprites.add(bullet)
        except IndexError:
            pass
        # Keep the player within screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

class Bullet(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = pygame.Surface((10, 20))  # Create a white rectangle for the bullet
        self.image.fill((255, 255, 255))  # Fill the rectangle with white color
        self.rect = self.image.get_rect()
        # Position the bullet at the top center of the player
        self.rect.centerx = player.rect.centerx
        self.rect.top = player.rect.top

    def update(self):
        # Move the bullet upward
        self.rect.y -= 15
        # Remove the bullet if it goes off-screen
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.image.load("monster.png")
        self.image = pygame.transform.scale(self.image, (60, 60))  # Scale the image to a smaller size
        self.rect = self.image.get_rect()
        self.rect.center = (x, 30)

    def update(self):
        global enemy_spawn_time
        # Move the enemy downward
        self.rect.y += 5
        # Remove the enemy if it goes off-screen
        if self.rect.bottom > screen_height:
            gameOver()
        


class Text(pygame.sprite.Sprite):
    def __init__(self, x, y, font, font_size, text, color):
        super().__init__()
        self.font = pygame.font.SysFont(font, font_size)
        self.image = self.font.render(text, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, direction=None):
        if direction == "up":
            self.rect.y -= 1
        elif direction == "down":
            self.rect.y += 1
        elif direction == "kill":
            self.kill()

# Create a sprite group for all sprites
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
game_header = Text(screen_width/2, screen_height/2, "Impact", 90, "Star Blaster", (255, 255, 255))
press_start = Text(screen_width/2, screen_height/2 + 90, "Impact", 30, "Press The Button on Your Controller to Start", (255, 255, 255))
all_sprites.add(game_header)
all_sprites.add(press_start)
dir_up = True
distance_of_text = 10
counter = 0


while not start:
    if dir_up:
        game_header.update("up")
    else:
        game_header.update("down")

    if counter == distance_of_text:
        dir_up = not dir_up
        counter = 0
    counter += 1

    # Takes event and breaks the while loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            start = True
            running = False 
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            start = True
            running = False

    if ser.in_waiting:
        inoInput = ser.readline().decode('utf-8', errors='ignore').strip()
        try:
            inputArr = list(map(int, inoInput.split(" ")))
        except ValueError:
            print(f"Invalid input: {inoInput}")
            inputArr = [0, 0, 0]

        if len(inputArr) == 3 and inputArr[2] == 1:
            start = True
    
        # Draw the background
    screen.blit(background, (0, 0))

    # Draw all sprites
    all_sprites.draw(screen)

    # Update the display
    pygame.display.update()


game_header.update("kill")
press_start.update("kill")

# add the player
player = Player(screen_width/2, screen_height)
all_sprites.add(player)

# initialize time global variables
shot_time = time.time() + 2 # to avoid the first shot immediately
enemy_spawn_time = time.time() + 5 # to avoid the first enemy spawn immediately



# Game loop
while running:

    # Takes event and breaks the while loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            running = False

    if ser.in_waiting:
        inoInput = ser.readline().decode('utf-8', errors='ignore').strip()
        try:
            inputArr = list(map(int, inoInput.split(" ")))
        except ValueError:
            print(f"Invalid input: {inoInput}")
            inputArr = [0, 0, 0]
        player.updatePlayer(inputArr)

    # Update all sprites
    all_sprites.update()

    # Draw the background
    screen.blit(background, (0, 0))

    # Draw all sprites
    all_sprites.draw(screen)
    gameOver()
    # Update the display
    pygame.display.update()


# Quit Pygame
pygame.quit()
sys.exit()
