from PIL import Image
import argparse
import os
import pygame


def load_image(name):
    fullname = name
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    return image


def OneMakesYouLarger(image_name, zoom=2):
    image = Image.open(image_name)
    pixels = image.load()
    x, y = image.size
    new_image = Image.new('RGBA', (x * zoom, y * zoom), (255, 255, 255, 255))
    new_pixels = new_image.load()
    for i in range(x):
        for j in range(y):
            for k in range(zoom):
                for l in range(zoom):
                    new_pixels[i * zoom + k, j * zoom + l] = pixels[i, j]
    imn = image_name.split('.')
    imn = imn[0] + '_temp.' +imn[1]
    new_image.save(imn)
    return load_image(imn)


class Tile(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__(all_sprites)
        self.image = OneMakesYouLarger(image)
        self.rect = self.image.get_rect().move(0, 0)

    def changeImage(self, img):
        self.image = OneMakesYouLarger(img)
        self.rect = self.image.get_rect().move(0, 0)

 


parser = argparse.ArgumentParser()
parser.add_argument('files', metavar='files', default=['no args'], nargs=2)
args = parser.parse_args()
cwd = os.getcwd()
fn, nmf = args.files
alp = [fn.replace('0', str(i)) for i in range(int(nmf))]
pygame.init()
screen = pygame.display.set_mode((32, 32))
clock = pygame.time.Clock()
running = True
all_sprites = pygame.sprite.Group()
i = 0
t = Tile(alp[i])

while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    t.changeImage(alp[i])
    i = (i + 1) % len(alp)
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(len(alp))