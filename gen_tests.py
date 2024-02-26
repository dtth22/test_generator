# Not meant to be maintainable :(

from PIL import Image, ImageDraw, ImageFilter, ImageOps
import numpy as np

import random
import glob
import time
import math
# VARS

random.seed(time.time())

images = []
for f in sorted(glob.iglob("notebank_templates/*.png")):
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
	off_x_min = off_x
	off_x_max = off_x_min + int(l_width * 2)
	off_y_min = off_y
	off_y_max = off_y_min + l_height // 8
	off_x_next = random.randint(off_x_min, off_x_max)
	off_y_next = random.randint(off_y_min, off_y_max)
	if off_x_next > b_width - l_width:
		off_x_next = 0
		off_y_next += 64
	base.paste(layer, (off_x_next, off_y_next), mask=layer)
	off_x_next += l_width // 2
	return off_x_next, off_y_next

def gradify(im, m_color, gradient_magnitude=1.0, reverse=False):
	if im.mode != 'RGBA':
		im = im.convert('RGBA')
	width, height = im.size
	gradient = Image.new('L', (1, height), color=0xFF)
	for x in range(height):
		# gradient.putpixel((x, 0), 255-x)
		gradient.putpixel((0, x), int(128 * (1 - gradient_magnitude * (height - float(x) if reverse else float(x))/height)))
	alpha = gradient.resize(im.size)
	black_im = Image.new('RGBA', (width, height), color=m_color) # i.e. black	  
	black_im.putalpha(alpha)
	gradient_im = Image.alpha_composite(im, black_im)

	return gradient_im


def random_list_with_fixed_sum(size, sum):
	p = []
	for _ in range(size):
		p.append(random.randint(0, sum))
	p.append(sum)
	p = sorted(p)

	a = [None] * size
	a[0] = p[0]
	for i in range(1, size):
		a[i] = p[i] - p[i - 1]

	return a

begin = 4
for i in range(8192):
	background = backgrounds[ random.randint(0, len(backgrounds) - 1) ].copy()

	total_value = 0
	sz = random.randint(25, 25)
	# Banknotes of higher value appear less frequently!
	cnt = sorted(random_list_with_fixed_sum(len(images), sz))[::-1]

	print(cnt)

	off_x_min = 0
	off_y_min = 0
	for i in range(len(images)):
		for _ in range(cnt[i]):
			img = images[i].copy()
			value = nb_value[i]
			rotated_img = rotate_randomly(img)
			distorted_im = distort_randomly(rotated_img)
			off_x_min, off_y_min = paste_randomly(background, distorted_im, off_x_min, off_y_min)
			total_value += value

	print(total_value)

	# background = gradify(background, ( random.randint(0, 255), random.randint(0, 255), random.randint(0, 255) ))
	# background = gradify(background, ( random.randint(0, 255), random.randint(0, 255), random.randint(0, 255) ), 1.0, True)

	background.show()
	# dir = "./subtask1/" + '{:02}'.format(begin + i) + ".jpg"
	# os.system("touch " + dir)
	# image = image.save(dir)
