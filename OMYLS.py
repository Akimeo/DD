from PIL import Image


def OneMakesYouLarger(image_name, zoom):
    image = Image.open(image_name + '.png')
    pixels = image.load()
    x, y = image.size
    new_image = Image.new('RGBA', (x * zoom, y * zoom), (255, 255, 255, 255))
    new_pixels = new_image.load()
    for i in range(x):
        for j in range(y):
            for k in range(zoom):
                for l in range(zoom):
                    new_pixels[i * zoom + k, j * zoom + l] = pixels[i, j]
    new_image.save(image_name + '.png')


def OneMakesYouSmaller(image_name, zoom):
    image = Image.open(image_name + '.png')
    pixels = image.load()
    x, y = image.size
    new_image = Image.new('RGBA', (x // zoom, y // zoom), (255, 255, 255, 255))
    new_pixels = new_image.load()
    for i in range(x // zoom):
        for j in range(y // zoom):
            new_pixels[i, j] = pixels[i * zoom, j * zoom]
    new_image.save(image_name + '.png')


OneMakesYouLarger('life', 2)
#OneMakesYouSmaller('CharF', 2)
