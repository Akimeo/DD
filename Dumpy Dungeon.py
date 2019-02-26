import sys
import pygame
from random import randint
from os.path import join


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites, player_group)
        self.image = char_images['charR0']
        self.rect = pygame.Rect(pos[0] * 32, BAR_HEIGHT + pos[1] * 32, 32, 32)
        self.mask = mask('char')
        self.direction = 0
        self.dirs = ['F', 'R', 'B', 'R']
        self.animation = 0


    def move(self, x, y):
        check = False
        self.rect.x += x
        self.rect.y += y
        for door in doors_group:
            if pygame.sprite.collide_mask(self, door):
                check = True
                break
        if pygame.sprite.spritecollideany(self, walls_group) or check:
            for sprite in walls_group:
                if pygame.sprite.collide_mask(self, sprite) or check:
                    self.rect.x -= x
                    self.rect.y -= y
                    break
        if x > 0:
            self.direction = 3
        elif x < 0:
            self.direction = 1
        elif y > 0:
            self.direction = 0
        elif y < 0:
            self.direction = 2
        if self.rect.x > WIDTH:
            camera.update((-1, 0))
        elif self.rect.x + self.rect[2] < 0:
            camera.update((1, 0))
        if self.rect.y > HEIGHT:
            camera.update((0, -1))
        elif self.rect.y + self.rect[3] < BAR_HEIGHT:
            camera.update((0, 1))
            

    def update(self):
        self.animation = (self.animation + 1) % FPS
        self.image = char_images['char' + self.dirs[self.direction] + str(self.animation // (FPS // 4))]
        if self.direction == 1:
            self.image = pygame.transform.flip(self.image, True, False)
        if pygame.sprite.spritecollideany(self, monsters_group):
            for sprite in monsters_group:
                if pygame.sprite.collide_mask(self, sprite):
                    health_bar.recieve_damage()


        
    def get_x(self):
        return self.rect.x


class Skull(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites, monsters_group)
        self.image = monster_images['skull0']
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * 32
        self.rect.y = pos[1] * 32 + BAR_HEIGHT
        self.mask = pygame.mask.from_surface(self.image)
        self.dir_x = 1
        self.dir_y = 1
        self.animation = 0
        self.speed = 2

    def update(self):
        self.rect.x += self.speed * self.dir_x
        self.rect.y += self.speed * self.dir_y
        if pygame.sprite.spritecollideany(self, walls_group) or \
                pygame.sprite.spritecollideany(self, doors_group):
            if self.rect.x < 33 or self.rect.x > 480:
                self.dir_x *= (-1)
            if self.rect.y < 97 or self.rect.y > 416:
                self.dir_y *= (-1)
            self.rect.x -= self.speed * self.dir_x * (-1)
            self.rect.y -= self.speed * self.dir_y * (-1)
        self.animation = (self.animation + 1) % FPS
        self.image = monster_images['skull' + str(self.animation // (FPS // 4))]
        if self.dir_x == -1:
            self.image = pygame.transform.flip(self.image, True, False)


class HealthBar(pygame.sprite.Sprite):
    def __init__(self):
        self.HP = 6

    def recieve_damage(self):
        self.HP -= 1
        if self.HP == 0:
            terminate()
        j = 0
        k = 0
        for i in range(self.HP):
            k += 1
            if k == 2 or i == (self.HP - 1):
                l = 0
                for sprite in health_bar_group:
                    if l == j:
                        sprite.update(k)
                    l += 1
                j += 1
                k = 0


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.count = 0
        self.updating = False

    def apply(self, obj):
        obj.rect.x += self.dx * TILE_WIDTH
        obj.rect.y += self.dy * TILE_HEIGHT

    def tick(self):
        self.count += 1
        if self.count > 15:
            self.updating = False
            self.count = 0

    def update(self, d):
        if d[1]:
            self.count = 4
        self.updating = True
        self.dx = d[0]
        self.dy = d[1]

    def is_updating(self):
        return self.updating


class HP(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        super().__init__(all_sprites, health_bar_group)
        self.image = toolbar_images['full_heart']
        self.rect = self.image.get_rect()
        self.rect.x = self.rect[2] * pos_x
        self.rect.y = 0

    def update(self, hp):
        if hp == 1:
            self.image = toolbar_images['half_heart']
        elif hp == 0:
            self.image = toolbar_images['empty_heart']


class Floor(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites, tiles_group)
        self.image = tile_images['floor_tile']
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * self.rect[2]
        self.rect.y = BAR_HEIGHT + pos[1] * self.rect[3]


class Wall(pygame.sprite.Sprite):
    def __init__(self, type, pos):
        super().__init__(all_sprites, tiles_group, walls_group)
        self.mask = mask('full')
        if type == 'top':
            self.image = wall_images['top' + str(randint(0, 2))]
        elif type == 'bot':
            self.image = wall_images['bot' + str(randint(0, 1))]
            self.mask = mask('bot')
        else:
            if pos[1] == -1 or pos[1] == 11 or pos[1] == 23:
                self.image = wall_images['wall2']
            else:
                self.image = wall_images['wall' + str(randint(0, 1))]
            if type == 'right':
                self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * TILE_WIDTH
        self.rect.y = pos[1] * TILE_HEIGHT + BAR_HEIGHT

class Door(pygame.sprite.Sprite):
    def __init__(self, type, pos_x, pos_y):
        super().__init__(all_sprites, tiles_group, doors_group)
        self.type = type
        self.image = door_images[self.type]
        self.rect = self.image.get_rect()
        self.rect.x = pos_x * TILE_WIDTH
        self.rect.y = BAR_HEIGHT + pos_y * TILE_HEIGHT
        self.mask = door_masks[self.image]
        self.state = True

    def update(self):
        if self.state:
            if self.type == 'lf':
                self.image = door_images['rbs']
            elif self.type == 'rf':
                self.image = door_images['lbs']
            elif self.type == 'lts':
                self.image = door_images['rf']
                self.rect.y -= TILE_HEIGHT // 2
            elif self.type == 'lbs':
                self.image = pygame.transform.flip(
                    door_images['lf'], True, False)
            elif self.type == 'rts':
                self.image = door_images['lf']
                self.rect.y -= TILE_HEIGHT // 2
            else:
                self.image = pygame.transform.flip(
                    door_images['rf'], True, False)
        else:
            self.image = door_images[self.type]
            if self.type == 'lts' or self.type == 'rts':
                self.rect.y += TILE_HEIGHT // 2
        if self.image in door_masks:
            self.mask = door_masks[self.image]
        else:
            self.mask = mask('bot')
        self.state = not self.state


def terminate():
    pygame.quit()
    sys.exit()

def make_statusbar():
    for i in range(3):
        HP(i)

def load_room(filename):
    filename = join('data', 'rooms', filename)
    with open(filename, 'r') as mapFile:
        room_map = [line.strip() for line in mapFile]
    max_width = max(map(len, room_map))
    return list(map(lambda x: x.ljust(max_width, '.'), room_map))

def make_room(room, dx, dy):
    for i in range(4):
        for j in range(4):
            Floor((i + 4 * dx, j + 4 * dy))
    for y in range(len(room)):
        for x in range(len(room[y])):
            if room[y][x] == '#':
                if x == 0:
                    type = 'left'
                elif x == len(room[y]) - 1:
                    type = 'right'
                elif y == 0:
                    type = 'top'
                else:
                    type = 'bot'
                Wall(type, (x + 16 * dx, y + 12 * dy))
            elif room[y][x] == '|':
                if y == 0 or y == len(room) - 1:
                    if x == 7:
                        Door('lf', x + 16 * dx, y + 12 * dy)
                    else:
                        Door('rf', x + 16 * dx, y + 12 * dy)
                elif x == 0:
                    if y == 5:
                        Door('lts', x + 16 * dx, y + 12 * dy)
                    else:
                        Door('lbs', x + 16 * dx, y + 12 * dy)
                else:
                    if y == 5:
                        Door('rts', x + 16 * dx, y + 12 * dy)
                    else:
                        Door('rbs', x + 16 * dx, y + 12 * dy)
            elif room[y][x] == '*':
                Skull((x + 16 * dx, y + 12 * dy))


def make_level():
    make_room(load_room('room_0.txt'), 0, 0)
    make_room(load_room('room_n.txt'), 0, -1)
    make_room(load_room('room_e.txt'), 1, 0)
    make_room(load_room('room_s.txt'), 0, 1)
    make_room(load_room('room_w.txt'), -1, 0)
    return Player((6, 6))


pygame.init()
SIZE = WIDTH, HEIGHT = 512, 448
BAR_WIDTH, BAR_HEIGHT = 512, 64
TILE_WIDTH, TILE_HEIGHT = 32, 32
screen = pygame.display.set_mode(SIZE)

char_images = {'char' + h + str(n):pygame.image.load(join('data', 'char2', 'char' + h + str(n) + '.png'))  for n in range(4) for h in ['R', 'B', 'F']}

monster_images = {
               'skull' + str(i): pygame.image.load(join('data', 'monsters', 'skull', 'skull' + str (i) + '.png')) for i in range(4)
}
toolbar_images = {
    'full_heart': pygame.image.load(join('data', 'interface', 'full_heart.png')),
    'half_heart': pygame.image.load(join('data', 'interface', 'half_heart.png')),
    'empty_heart': pygame.image.load(join('data', 'interface', 'empty_heart.png'))}
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
    'bot1': pygame.image.load(join('data', 'tiles', 'bot_wall_tile_1.png'))
}
door_images = {
    'lf': pygame.image.load(join('data', 'tiles', 'lf_door_tile.png')),
    'rf': pygame.image.load(join('data', 'tiles', 'rf_door_tile.png')),
    'lts': pygame.image.load(join('data', 'tiles', 'side_door_tile.png')),
    'lbs': pygame.transform.flip(pygame.image.load(
        join('data', 'tiles', 'side_door_tile.png')), False, True),
    'rts': pygame.transform.flip(pygame.image.load(
        join('data', 'tiles', 'side_door_tile.png')), True, False),
    'rbs': pygame.transform.flip(pygame.image.load(
        join('data', 'tiles', 'side_door_tile.png')), True, True)
}

mask = lambda x: pygame.mask.from_surface(pygame.image.load(join('data',
                                                                 'tiles',
                                                                 'masks',
                                                                 x + '.png')))
door_masks = {
    door_images['lf']: mask('bot'), door_images['rf']: mask('bot'),
    door_images['rts']: mask('side_l'), door_images['rbs']: mask('side_l'),
    door_images['lts']: mask('side_r'), door_images['lbs']: mask('side_r')
}

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
monsters_group = pygame.sprite.Group()
health_bar_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
doors_group = pygame.sprite.Group()

player = make_level()
make_statusbar()

FPS = 60
clock = pygame.time.Clock()

pygame.mixer.music.load(join('data', 'music', 'music.WAV'))
pygame.mixer.music.play()

camera = Camera()
check = 0

health_bar = HealthBar()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key == 101:
                doors_group.update()
    if camera.is_updating():
        for sprite in tiles_group:
            camera.apply(sprite)
        for sprite in player_group:
            camera.apply(sprite)
        for sprite in monsters_group:
            camera.apply(sprite)
        camera.tick()
    else:
        keys = pygame.key.get_pressed()
        if keys[273] or keys[119]:
            player.move(0, -TILE_HEIGHT // 16)
        if keys[274] or keys[115]:
            player.move(0, TILE_HEIGHT // 16)
        if keys[275] or keys[pygame.K_d]:
            player.move(TILE_WIDTH // 16, 0)
        if keys[276] or keys[97]:
            player.move(-TILE_WIDTH // 16, 0)
    screen.fill((255, 255, 255))
    player_group.update()
    monsters_group.update()
    all_sprites.draw(screen)
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, BAR_WIDTH, BAR_HEIGHT))
    health_bar_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
