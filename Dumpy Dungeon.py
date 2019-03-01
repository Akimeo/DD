import sys
import pygame
from random import randint
from os.path import join
from time import sleep


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, player_group)
        self.image = char_images['charR0']
        self.rect = pygame.Rect(240, 240, 32, 32)
        self.mask = mask('char')
        self.direction = 0
        self.dirs = ['F', 'R', 'B', 'R']
        self.animation = 0
        self.m_anim = ''
        self.m_anim_t = 0
        self.invincible = False
        self.timer = 0
        self.room = (0, 0)

    def move(self, x, y):
        print(self.room)
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
            self.room = (self.room[0] + 1, self.room[1])
        elif self.rect.x + self.rect[2] < 0:
            camera.update((1, 0))
            self.room = (self.room[0] - 1, self.room[1])
        if self.rect.y > HEIGHT:
            camera.update((0, -1))
            self.room = (self.room[0], self.room[1] - 1)
        elif self.rect.y + self.rect[3] < BAR_HEIGHT:
            camera.update((0, 1))
            self.room = (self.room[0], self.room[1] + 1)
        if self.m_anim_t == 10:
            self.m_anim_t = 0
            if self.m_anim != 'R':
                self.m_anim = 'R'
            else:
                self.m_anim = 'L'

    def attack(self):
        DamageWave(self.rect.x, self.rect.y, self.direction)

    def update(self):
        self.m_anim_t += 1
        if self.m_anim_t == 20:
            self.m_anim_t = 0
            self.m_anim = ''
        if self.invincible:
            self.timer += 1
            if self.timer == FPS:
                self.invincible = False
                self.timer = 0
        self.animation = (self.animation + 1) % FPS
        if self.invincible and (self.animation in range(0, 13) or self.animation in range(24, 37) or self.animation in range(48, 61)):
            self.image = char_images['damaged']
        else:
            self.image = char_images['char' + self.dirs[self.direction] + str(self.animation // (FPS // 4)) + self.m_anim]
        if self.direction == 1:
            self.image = pygame.transform.flip(self.image, True, False)
        if pygame.sprite.spritecollideany(self, monsters_group):
            oldmask = self.mask
            self.mask = pygame.mask.from_surface(self.image)
            for sprite in monsters_group:
                if pygame.sprite.collide_mask(self, sprite):
                    if not self.invincible:
                        damage.play()
                        health_bar.recieve_damage()
                        self.animation = 0
                        self.invincible = True
            self.mask = oldmask
        
    def get_x(self):
        return self.rect.x


class DamageWave(pygame.sprite.Sprite):
    def __init__(self, x, y, d):
        super().__init__(projectile_group)
        self.image = interface_images['dmg_wave']
        self.rect = self.image.get_rect()
        if d == 0:
            self.d = (0, 1)
            self.image = pygame.transform.rotate(self.image, 270)
            self.image = pygame.transform.flip(self.image, True, False)
        elif d == 1:
            self.d = (-1, 0)
            self.image = pygame.transform.flip(self.image, True, False)
        elif d == 2:
            self.d = (0, -1)
            self.image = pygame.transform.rotate(self.image, 90)
        else:
            self.d = (1, 0)
        self.rect.x, self.rect.y = x + 24 * self.d[0], y + 24 * self.d[1]
        self.mask = pygame.mask.from_surface(self.image)
        self.duration = 0

    def update(self):
        self.duration += 1
        self.rect.x, self.rect.y = player.rect.x + 24 * self.d[0], player.rect.y + 24 * self.d[1]
        if self.duration == 20:
            projectile_group.remove(self)


class Fire(pygame.sprite.Sprite):
    def __init__(self, s_pos, p_pos):
        super().__init__(enemy_projectile_group)
        self.image = interface_images['fire']
        self.rect = self.image.get_rect()
        self.x, self.y = self.rect.x, self.rect.y = s_pos
        self.mask = pygame.mask.from_surface(self.image)
        self.p_pos = (p_pos[0] + 16 - s_pos[0], p_pos[1] + 16 - s_pos[1])
        self.duration = 0
        self.animation = 0

    def update(self):
        self.duration += 1
        self.animation += 1
        if self.animation == 15:
            self.animation = 0
            self.image = pygame.transform.flip(self.image, True, False)
        self.x += self.p_pos[0] / FPS
        self.y += self.p_pos[1] / FPS
        self.rect.x, self.rect.y = int(self.x), int(self.y)
        if self.duration == 60:
            enemy_projectile_group.remove(self)
        if pygame.sprite.spritecollideany(self, player_group):
                for sprite in player_group:
                    if pygame.sprite.collide_mask(self, sprite):
                        if not player.invincible:
                            damage.play()
                            health_bar.recieve_damage()
                            player.animation = 0
                            player.invincible = True
                            enemy_projectile_group.remove(self)
        if pygame.sprite.spritecollideany(self, projectile_group):
                for sprite in projectile_group:
                    if pygame.sprite.collide_mask(self, sprite):
                        enemy_projectile_group.remove(self)


class Skull(pygame.sprite.Sprite):
    def __init__(self, pos, room):
        super().__init__(all_sprites, monsters_group)
        self.room = room
        self.image = monster_images['skull0']
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * 32
        self.rect.y = pos[1] * 32 + BAR_HEIGHT
        self.mask = pygame.mask.from_surface(self.image)
        self.dx = self.dy = 1
        self.animation = 0
        self.speed = 2
        self.firerate = 0
        self.active = 0

    def update(self):
        self.animation = (self.animation + 1) % FPS
        self.image = monster_images['skull' + str(self.animation // (FPS // 4))]
        if self.active == 30:
            dx, dy = self.dx, self.dy
            self.rect.x += self.speed * dx
            self.rect.y += self.speed * dy
            for sprite in doors_group:
                if pygame.sprite.collide_rect(self, sprite) and pygame.sprite.collide_mask(self, sprite):
                    collides = True
                    if sprite.type in ['lf', 'rf']:
                        self.dy *= -1
                    else:
                        self.dx *= -1
                    break
            for sprite in walls_group:
                if pygame.sprite.collide_rect(self, sprite) and pygame.sprite.collide_mask(self, sprite):
                    if "collides" not in locals():
                        collides = True
                        if sprite.type in ['top', 'bot']:
                            self.dy *= -1
                        else:
                            self.dx *= -1
                        break
            if "collides" in locals():
                self.rect.x -= self.speed * dx
                self.rect.y -= self.speed * dy
            if dx == -1:
                self.image = pygame.transform.flip(self.image, True, False)
            if abs(player.rect.x - self.rect.x) < 128 and abs(player.rect.y - self.rect.y) < 128 and self.firerate < 0:
                self.firerate = 120
                fire.play()
                Fire((self.rect.x, self.rect.y), (player.rect.x, player.rect.y))
            self.firerate -= 1
        elif self.room == player.room:
            self.active += 1



class Mage(pygame.sprite.Sprite):
    def __init__(self, pos, room, type='r'):
        super().__init__(all_sprites, monsters_group)
        self.n_im = pygame.image.load(join('data', 'monsters', 'skl_mage', 'mage.png'))
        self.a_im = pygame.image.load(join('data', 'monsters', 'skl_mage', 'mage_at.png'))
        if type == 'l':
            self.n_im = pygame.transform.flip(self.n_im, True, False)
            self.a_im = pygame.transform.flip(self.a_im, True, False)
        self.image = self.n_im
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * 32
        self.rect.y = pos[1] * 32 + BAR_HEIGHT
        self.mask = mask("full")
        self.room = room
        self.animation = 0
        self.firerate = 0
        self.active = 0

    def update(self):
        if self.active > 30:
            if self.firerate < 0 and self.animation in range(30):
                self.firerate = 10
                fire.play()
                Fire((self.rect.x, self.rect.y), (player.rect.x, player.rect.y))
            elif self.firerate < 0 and self.animation < 0:
                self.animation = 60
            if self.animation > 0 and self.image != self.a_im:
                self.image = self.a_im
            elif self.animation < 0 and self.image != self.n_im:
                self.image = self.n_im
            self.firerate -= 1
            self.animation -= 1
            print(self.firerate, self.animation)
        elif self.room == player.room:
            self.active += 1


class Peaks(pygame.sprite.Sprite):
    def __init__(self, pos, room):
        super().__init__(all_sprites, trap_group)
        self.image = trap_images['peaks0']
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * 32
        self.rect.y = pos[1] * 32 + BAR_HEIGHT
        self.mask = pygame.mask.from_surface(self.image)
        self.animation = 0
        self.room = room

    def update(self):
        if self.animation == 0 and self.room == player.room:
            spiketrap.play()
        self.animation = (self.animation + 1) % (FPS * 4)
        self.image = trap_images['peaks' + str(self.animation // FPS)]
        if self.animation < 120:
            if pygame.sprite.spritecollideany(self, player_group):
                for sprite in player_group:
                    if pygame.sprite.collide_mask(self, sprite):
                        if not player.invincible:
                            damage.play()
                            health_bar.recieve_damage()
                            player.animation = 0
                            player.invincible = True


class HP(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        self.num = pos_x * 2
        super().__init__(all_sprites, health_bar_group)
        self.image = toolbar_images['full_heart']
        self.rect = self.image.get_rect()
        self.rect.x = 16 + (self.rect[2] + 2) * pos_x
        self.rect.y = 34

    def update(self, hp):
        hp = hp - self.num
        if hp == 1:
            self.image = toolbar_images['half_heart']
        elif hp == 0:
            self.image = toolbar_images['empty_heart']


class HealthBar(pygame.sprite.Sprite):
    def __init__(self):
        self.HP = 12

    def recieve_damage(self):
        self.HP -= 1
        if self.HP == 0:
            pmm.load("data/music/game_over.mp3")
            pmm.play()
            while pmm.get_busy():
                player.invincible = True
                player.timer = 0
                player.update()
                all_sprites.draw(screen)
                clock.tick(FPS)
                pygame.display.flip()
            end_screen()
        health_bar_group.update(self.HP)


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
        self.type = type
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
        self.state = False
        self.previous_state = False

    def update(self, cheat=None):
        if self.state != self.previous_state:
            door_sound.play()
        if self.state or cheat:
            if self.type == 'lf':
                self.image = door_images['rbs']
            elif self.type == 'rf':
                self.image = door_images['lbs']
            elif self.type == 'lts':
                self.image = door_images['rf']
                if not self.previous_state and not cheat:
                    self.rect.y -= TILE_HEIGHT // 2
            elif self.type == 'lbs':
                self.image = pygame.transform.flip(
                    door_images['lf'], True, False)
            elif self.type == 'rts':
                self.image = door_images['lf']
                if not self.previous_state and not cheat:
                    self.rect.y -= TILE_HEIGHT // 2
            else:
                self.image = door_images['lf']
        else:
            if pygame.sprite.spritecollideany(self, player_group):
                for sprite in player_group:
                    if pygame.sprite.collide_mask(self, sprite):
                        if player.direction == 0:
                            player.move(0, -player_speed * 3)
                        elif player.direction == 1:
                            player.move(-player_speed * 12, 0)
                        elif player.direction == 2:
                            player.move(0, player_speed * 5)
                        else:
                            player.move(player_speed * 13, 0)
            self.image = door_images[self.type]
            if self.type == 'lts' or self.type == 'rts':
                if self.previous_state:
                    self.rect.y += TILE_HEIGHT // 2
        if self.image in door_masks:
            self.mask = door_masks[self.image]
        else:
            self.mask = mask('bot')
        self.previous_state = self.state

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


class Inputer:
    def __init__(self):
        self.str = ''
        self.worked = True


    def __getitem__(self, key):
        return self.str[len(self.str) - key:]


    def add(self, text):
        self.str += str(text)
        self.worked = True
        if len(self.str) > 255:
            self.str = self.str[len(self.str) - 255:]


def make_order(ord_group):
    ord_group.empty()
    sp_list = sorted(list(all_sprites), key=lambda sp: sp.rect.y if type(sp) not in (Floor, Peaks) else -1)
    ord_group.add(sp_list)
    return ord_group


def make_statusbar():
    for i in range(6):
        HP(i)


def start_screen():
    fon = pygame.image.load(join('data', 'interface', 'fon.png'))
    play = pygame.mixer.Sound(join('data', 'music', 'start_sfx.wav'))
    pmm.load(join('data', 'music', "SSBU_OP.mp3"))
    pmm.play()
    for i in range(16):
        for j in range(14):
            Floor((i, j))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                all_sprites.empty()
                walls_group.empty()
                tiles_group.empty()
                play.play()
                while pygame.mixer.get_busy():
                    sleep(0.8)
                return  # начинаем игру
        all_sprites.draw(screen)
        screen.blit(fon, (0, 0))
        pygame.display.flip()
        clock.tick(100)


def end_screen():
    fon = pygame.image.load(join('data', 'interface', 'endgame.png'))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                terminate()  # начинаем игру
        screen.blit(fon, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)


def win_screen():
    fon = pygame.image.load(join('data', 'interface', 'win_game.png'))
    pmm.load(join('data', 'music', "SSBU_OP.mp3"))
    pmm.play()
    ended = False
    h = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN] and ended:
                terminate()  # начинаем игру
        if h > 448 - 1400:
            screen.blit(fon, (0, h))
            h -= 1
        else:
            sleep(0.5)
            ended = True
        pygame.display.flip()
        clock.tick(FPS)

def make_level():
    make_room(load_room('room_0.txt'), 0, 0)
    make_room(load_room('room_n.txt'), 0, -1)
    make_room(load_room('room_e.txt'), 1, 0)
    make_room(load_room('room_s.txt'), 0, 1)
    make_room(load_room('room_w.txt'), -1, 0)
    return Player()


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
                Skull((x + 16 * dx, y + 12 * dy), (dx, -dy))
            elif room[y][x] == 'M':
                Mage((x + 16 * dx, y + 12 * dy), (dx, -dy))
            elif room[y][x] == 'm':
                Mage((x + 16 * dx, y + 12 * dy), (dx, -dy), 'l')
            elif room[y][x] == '+':
                Peaks((x + 16 * dx, y + 12 * dy), (dx, -dy))


def load_room(filename):
    filename = join('data', 'rooms', filename)
    with open(filename, 'r') as mapFile:
        room_map = [line.strip() for line in mapFile]
    max_width = max(map(len, room_map))
    return list(map(lambda x: x.ljust(max_width, '.'), room_map))


def terminate():
    pygame.quit()
    sys.exit()


def update_masked_avatar():
    surf = pygame.image.load("mask.png")
    surf.blit(pygame.image.load("avatar1.png"), (0, 0), None, pygame.BLEND_RGBA_MULT)
    return surf


pygame.init()
SIZE = WIDTH, HEIGHT = 512, 448
BAR_WIDTH, BAR_HEIGHT = 512, 0
TILE_WIDTH, TILE_HEIGHT = 32, 32
screen = pygame.display.set_mode(SIZE)
pmm = pygame.mixer.music
clock = pygame.time.Clock()
FPS = 60
check = 0
player_speed = 2
camera = Camera()

damage = pygame.mixer.Sound(join('data', 'music', 'Damage.ogg'))
hit = pygame.mixer.Sound(join('data', 'music', 'Hit.WAV'))
door_sound = pygame.mixer.Sound(join('data', 'music', 'Door.WAV'))
fire = pygame.mixer.Sound(join('data', 'music', 'Fire.WAV'))
spiketrap = pygame.mixer.Sound(join('data', 'music', 'Spiketrap.WAV'))

life = pygame.image.load(join('data', 'interface', 'life.png'))
char_images = {'char' + h + str(n) + k:pygame.image.load(join('data', 'char', 'char' + h + str(n) + k + '.png'))  for n in range(4) for h in ['R', 'B', 'F'] for k in ['', 'R', 'L']}
char_images['damaged'] = pygame.image.load(join('data', 'char', 'damaged.png'))

monster_images = {
    'skull' + str(i): pygame.image.load(join('data', 'monsters', 'skull', 'skull' + str (i) + '.png')) for i in range(4)
}
trap_images = {
    'peaks' + str(i): pygame.image.load(join('data', 'traps', 'peaks', 'peaks' + str (i) + '.png')) for i in range(4)
}
toolbar_images = {
    'full_heart': pygame.image.load(join('data', 'interface', 'full_heart.png')),
    'half_heart': pygame.image.load(join('data', 'interface', 'half_heart.png')),
    'empty_heart': pygame.image.load(join('data', 'interface', 'empty_heart.png'))}
interface_images = {'dmg_wave': pygame.image.load(join('data', 'interface', 'dmg_wave.png')),
                    'fire': pygame.image.load(join('data', 'interface', 'fire1.png'))}
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
trap_group = pygame.sprite.Group()
health_bar_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
doors_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()
enemy_projectile_group = pygame.sprite.Group()


start_screen()
BAR_HEIGHT = 64
player = make_level()
inputer = Inputer()
make_statusbar()

pmm.load(join('data', 'music', 'music.WAV'))
pmm.play(-1)

health_bar = HealthBar()

ordered = make_order(pygame.sprite.OrderedUpdates())
to_order = False
pause = False
unblocked = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            unblocked = True
            inputer.add(chr(event.key))
            if event.key == pygame.K_SPACE and not pause:
                hit.play()
                player.attack()
            if event.key == pygame.K_p:
                pause = not pause
                if pause:
                    pmm.pause()
                    pygame.mixer.pause()
                else:
                    pmm.unpause()
                    pygame.mixer.unpause()
    if not pause:
        if camera.is_updating():
            for sprite in tiles_group:
                camera.apply(sprite)
            for sprite in player_group:
                camera.apply(sprite)
            for sprite in monsters_group:
                camera.apply(sprite)
            for sprite in trap_group:
                camera.apply(sprite)
            camera.tick()
        else:
            keys = pygame.key.get_pressed()
            if keys[273] or keys[119]:
                player.move(0, -player_speed)
            if keys[274] or keys[115]:
                player.move(0, player_speed)
            if keys[275] or keys[pygame.K_d]:
                player.move(player_speed, 0)
            if keys[276] or keys[97]:
                player.move(-player_speed, 0)
        for dmg_wave in projectile_group:
            if pygame.sprite.spritecollideany(dmg_wave, monsters_group):
                for sprite in monsters_group:
                    if pygame.sprite.collide_mask(dmg_wave, sprite):
                        all_sprites.remove(sprite)
                        monsters_group.remove(sprite)
        screen.fill((255, 255, 255))
        closed = False
        for monster in monsters_group:
            if monster.room == player.room:
                closed = True
                break
        if closed:
            for door in doors_group:
                door.state = False
        else:
            for door in doors_group:
                door.state = True
        doors_group.update()
        player_group.update()
        monsters_group.update()
        trap_group.update()
        ordered = make_order(ordered)
        ordered.draw(screen)
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, BAR_WIDTH, BAR_HEIGHT))
        screen.blit(life, (16, 16))
        health_bar_group.draw(screen)
        projectile_group.draw(screen)
        projectile_group.update()
        enemy_projectile_group.draw(screen)
        enemy_projectile_group.update()
    else:
        pygame.draw.rect(screen, (255, 255, 255), (449, 16, 10, 32))
        pygame.draw.rect(screen, (255, 255, 255), (469, 16, 10, 32))
    if unblocked:
        unblocked = False
        if inputer[5] == 'skull':
            print('Cheat "Skull" activated!')
            Skull((randint(1, 14), randint(1, 10)), player.room)
        elif inputer[4] == 'door':
            print('Cheat "Door" activated!')
            doors_group.update(True)
    if inputer[3] == 'win' or not monsters_group:
        print('You won!')
        win_screen()
    clock.tick(FPS)
    pygame.display.flip()
 