import random
import glob
import time
import math
import os

from PIL import Image, ImageOps

DIR = "./subtask1/"
N_IMAGES = 2
MIN_NOTES_PER_IMG = 16
MAX_NOTES_PER_IMG = 25
APPLY_GRADIENT = True

random.seed(time.time())

images = []
for f in sorted(glob.iglob("note_templates/*.png")):
    image = Image.open(f).convert('RGBA')
    img_width, img_height = image.size
    aspect_ratio = (img_width / img_height)
    width = 320
    height = int(width / aspect_ratio)
    image = image.resize((width, height))
    images.append(image)

backgrounds = []
for f in sorted(glob.iglob("backgrounds/*.jpg")):
    image = Image.open(f)
    backgrounds.append(image)

nb_value = [1, 1, 2, 2, 5, 5, 10, 10, 20, 20, 50, 50, 100, 100, 200, 200, 500, 500]

class WaveDeformer:
    def transform(self, x, y, strength):
        y = y + strength*math.sin(x/40)
        return x, y
    def transform_rectangle(self, x0, y0, x1, y1, strength=10):
        return (*self.transform(x0, y0, strength),
      *self.transform(x0, y1, strength),
      *self.transform(x1, y1, strength),
      *self.transform(x1, y0, strength),
      )
    def getmesh(self, img):
        self.w, self.h = img.size
        gridspace = 20
        target_grid = []
        for x in range(0, self.w, gridspace):
            for y in range(0, self.h, gridspace):
                target_grid.append((x, y, x + gridspace, y + gridspace))
        strength = random.randint(2, 20)
        source_grid = [self.transform_rectangle(*rect, strength) for rect in target_grid]
        return [t for t in zip(target_grid, source_grid)]

def distort_randomly(im):
    return ImageOps.deform(im, WaveDeformer())

def rotate_randomly(im):
    return im.rotate(random.randint(0, 360), expand=True)

def paste_randomly(base, layer, off_x, off_y):
    b_width, b_height = base.size
    l_width, l_height = layer.size
    off_x = off_x
    off_x_max = off_x + int(l_width * 2)
    off_y = off_y
    off_y_max = off_y + l_height // 8
    off_x_next = random.randint(off_x, off_x_max)
    off_y_next = random.randint(off_y, off_y_max)
    if off_x_next > b_width - l_width:
        off_x_next = 0
        off_y_next += 64
    base.paste(layer, (off_x_next, off_y_next), mask=layer)
    coords = (off_x_next, off_y_next, off_x_next + layer.width, off_y_next + layer.height)
    off_x_next += l_width // 2
    return off_x_next, off_y_next, coords

def gradify(im, m_color, gradient_magnitude=1.0, reverse=False):
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    width, height = im.size
    gradient = Image.new('L', (1, height), color=0xFF)
    for x in range(height):
        gradient.putpixel((0, x), int(128 * (1 - gradient_magnitude * (height - float(x) if reverse else float(x))/height)))
    alpha = gradient.resize(im.size)
    black_im = Image.new('RGBA', (width, height), color=m_color) # i.e. black      
    black_im.putalpha(alpha)
    gradient_im = Image.alpha_composite(im, black_im)

    return gradient_im

def random_list_with_fixed_sum(size, sum_of_list):
    p = []
    for _ in range(size):
        p.append(random.randint(0, sum_of_list))
    p.append(sum_of_list)
    p = sorted(p)

    a = [None] * size
    a[0] = p[0]
    for i in range(1, size):
        a[i] = p[i] - p[i - 1]

    return a

os.system(f"mkdir {DIR} && mkdir {os.path.join(DIR, 'labels_detection/')}")

labels_dir = os.path.join(DIR, "labels.txt")
open(labels_dir, "w")

for i in range(N_IMAGES):
    filename = f"{i:>06}"
    img_dir = os.path.join(DIR, f"{filename}.png")

    labels_detection_dir = os.path.join(DIR, f"labels_detection/{filename}.txt")
    open(labels_detection_dir, "w")

    background = backgrounds[ random.randint(0, len(backgrounds) - 1) ].copy()

    total_value = 0
    sz = random.randint(MIN_NOTES_PER_IMG, MAX_NOTES_PER_IMG)
    cnt = sorted(random_list_with_fixed_sum(len(images), sz))[::-1] # Banknotes of higher value appear less frequently

    off_x = 0
    off_y = 0
    for i, img in enumerate(images):
        for _ in range(cnt[i]):
            rotated_img = rotate_randomly(img)
            distorted_img = distort_randomly(rotated_img)
            off_x, off_y, coords = paste_randomly(background, distorted_img, off_x, off_y)
            value = nb_value[i]
            total_value += value
            with open(labels_detection_dir, "a") as f:
                x0, y0, x1, y1 = coords
                f.write(f"{value * 1000} {x0} {y0} {x1} {y1}\n")

    with open(labels_dir, "a") as f:
        f.write(f"{filename},{total_value * 1000}\n")

    if APPLY_GRADIENT:
        background = gradify(background, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        background = gradify(background, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 1.0, True)

    background.save(img_dir)
    print(f"New image saved at {img_dir}")
