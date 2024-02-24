from PIL import Image, ImageDraw, ImageFilter, ImageOps

import random
import glob
import time
import math
# VARS

background_img_path = "third_party/background.jpg"

im1 = Image.open(background_img_path)
images = []

random.seed(time.time())

for f in sorted(glob.iglob("notebank_templates/*.png")):
	images.append(Image.open(f).convert('RGBA'))
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

def paste_randomly(base, layer, is_clipping=False):
	b_width, b_height = base.size
	l_width, l_height = layer.size
	off_x_min = -1*l_width//2 if is_clipping else 0
	off_x_max = b_width - l_width//2 if is_clipping else b_width - l_width
	off_y_min = -1*l_height//2 if is_clipping else 0
	off_y_max = b_height - l_height//2 if is_clipping else b_height - l_height
	base.paste(layer, (random.randint(off_x_min, off_x_max), random.randint(off_y_min, off_y_max)), mask=layer)

def gradify(im, m_color, gradient_magnitude=1.0, reverse=False):
	if im.mode != 'RGBA':
		im = im.convert('RGBA')
	width, height = im.size
	gradient = Image.new('L', (1, height), color=0xFF)
	for x in range(height):
		# gradient.putpixel((x, 0), 255-x)
		gradient.putpixel((0, x), int(150 * (1 - gradient_magnitude * (height - float(x) if reverse else float(x))/height)))
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


sz = random.randint(16, 32)
cnt = random_list_with_fixed_sum(18, sz)

total_value = 0

for i in range(18):
	img = images[i]
	value = nb_value[i]
	for _ in range(cnt[i]):
		rotated_img = rotate_randomly(img)
		distorted_im = distort_randomly(rotated_img)
		paste_randomly(im1, distorted_im, True)
		total_value += value

print(total_value)


gradient_img = gradify(im1, (0, 0, 0))
gradient_img = gradify(gradient_img, (255, 255, 255), 1.0, True)

gradient_img.show()
