import sys
import pygame
from random import randint
from os.path import join


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)
        self.image = char_images['char0']
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * self.rect[2]
        self.rect.y = BAR_HEIGHT + pos[1] * self.rect[3]
        self.direction = 1
        self.animation = 0

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y
        if pygame.sprite.spritecollideany(self, walls_group):
            self.rect.x -= x
            self.rect.y -= y
        if x != 0 and self.direction != (x < 0):
            self.image = pygame.transform.flip(self.image, True, False)
            self.direction = not self.direction

    def update(self):
        self.animation = (self.animation + 1) % FPS
        self.image = char_images['char' + str(self.animation // (FPS // 4))]
        if self.direction:
            self.image = pygame.transform.flip(self.image, True, False)


class HP(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        super().__init__(all_sprites, statusbar_group)
        self.image = toolbar_images['full_heart']
        self.rect = self.image.get_rect()
        self.rect.x = self.rect[2] * pos_x
        self.rect.y = 0


class Floor(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)
        self.image = tile_images['floor_tile']
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * self.rect[2] + TILE_WIDTH
        self.rect.y = BAR_HEIGHT + pos[1] * self.rect[3] + TILE_HEIGHT


class Wall(pygame.sprite.Sprite):
    def __init__(self, type, pos):
        super().__init__(all_sprites, walls_group)
        if type == 'top':
            self.image = wall_images['top' + str(randint(0, 2))]
        elif type == 'bot':
            self.image = wall_images['bot' + str(randint(0, 1))]
        else:
            if pos == 13:
                self.image = wall_images['wall2']
            else:
                self.image = wall_images['wall' + str(randint(0, 1))]
            if type == 'right':
                self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        if type == 'top':
            self.rect.x = pos * TILE_WIDTH
            self.rect.y = BAR_HEIGHT
        elif type == 'bot':
            self.rect.x = pos * TILE_WIDTH
            self.rect.y = HEIGHT - TILE_HEIGHT
        elif type == 'left':
            self.rect.x = 0
            self.rect.y = BAR_HEIGHT + pos * TILE_HEIGHT
        else:
            self.rect.x = WIDTH - TILE_WIDTH
            self.rect.y = BAR_HEIGHT + pos * TILE_HEIGHT


def terminate():
    pygame.quit()
    sys.exit()

def make_toolbar():
    for i in range(3):
        HP(i)

def make_room():
    for i in range(4):
        for j in range(4):
            Floor((i, j))
    for i in range(16):
        Wall('top', i + 1)
        Wall('bot', i + 1)
    for i in range(14):
        Wall('left', i)
        Wall('right', i)
    player = Player((3, 3))
    return player


pygame.init()
SIZE = WIDTH, HEIGHT = 576, 504
BAR_WIDTH, BAR_HEIGHT = 576, 56
TILE_WIDTH, TILE_HEIGHT = 32, 32
screen = pygame.display.set_mode(SIZE)

char_images = {'char0': pygame.image.load(join('data', 'char2', 'char0.png')),   
               'char1': pygame.image.load(join('data', 'char2', 'char1.png')),
               'char2': pygame.image.load(join('data', 'char2', 'char2.png')),
               'char3': pygame.image.load(join('data', 'char2', 'char3.png'))}
toolbar_images = {
    'full_heart': pygame.image.load(join('data', 'interface', 'full_heart.png'))}
tile_images = {'floor_tile': pygame.image.load(
    join('data', 'tiles', 'floor_tile.png'))}
wall_images = {
    'wall0': pygame.image.load(join('data', 'tiles', 'wall_tile_0.png')),
    'wall1': pygame.image.load(join('data', 'tiles', 'wall_tile_1.png')),
    'wall2': pygame.image.load(join('data', 'tiles', 'wall_tile_2.png')),
    'top0': pygame.image.load(join('data', 'tiles', 'top_wall_tile_0.png')),
    'top1': pygame.image.load(join('data', 'tiles', 'top_wall_tile_1.png')),
    'top2': pygame.image.load(join('data', 'tiles', 'top_wall_tile_2.png')),
    'bot0': pygame.image.load(join('data', 'tiles', 'bot_wall_tile_0.png')),
    'bot1': pygame.image.load(join('data', 'tiles', 'bot_wall_tile_1.png'))}

all_sprites = pygame.sprite.Group()
statusbar_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()

make_toolbar()
player = make_room()

FPS = 60
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                player.move(0, TILE_HEIGHT)
            if event.key == pygame.K_UP:
                player.move(0, -TILE_HEIGHT)
            if event.key == pygame.K_RIGHT:
                player.move(TILE_WIDTH, 0)
            if event.key == pygame.K_LEFT:
                player.move(-TILE_WIDTH, 0)
            if event.key == pygame.K_d:
                for wall in walls_group:
                    all_sprites.remove(wall)
                    
    screen.fill((37, 19, 26))
    all_sprites.draw(screen)
    all_sprites.update()
    clock.tick(FPS)
    pygame.display.flip()
