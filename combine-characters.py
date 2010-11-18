from urllib import urlopen
import sys, os, re, math
from PIL import Image, ImageDraw, ImageFont

chardir = '../char_files/'
pagedir = '../page_files/'
block_names_url = 'http://www.unicode.org/Public/6.0.0/ucd/Blocks.txt'
font_file = '/usr/share/fonts/truetype/ttf-bitstream-vera/VeraBd.ttf'
if not os.path.isdir(pagedir):
	os.mkdir(pagedir)

if len(sys.argv) < 5:
	print 'Usage: python combine-characters.py <width> <height> <width in pages> <characters per line on one page> <margin>'
	sys.exit()

page_width = int(sys.argv[1])
page_height = int(sys.argv[2])

margin = int(sys.argv[5])
image_width = page_width - 2 * margin
image_height = page_height - 2 * margin

pages_width = int(sys.argv[3])
cols_per_page = int(sys.argv[4])

char_width = float(image_width)/cols_per_page
char_height = 160 * char_width/126

rows_per_page = image_height / int(char_height + 3*char_height/20.)

char_height = int((20./23) * image_height/rows_per_page)
label_height = char_height/4

cur_files = set(os.listdir('.'))
if 'Blocks.txt' not in cur_files:
	file('Blocks.txt', 'w').write(urlopen(block_names_url).read())

with open('Blocks.txt', 'r') as f:
	block_lines = f.read()

matches = re.findall('([0-9A-F]{4,5})(.*; +)(.+)', block_lines)

block_labels = dict()
for x in matches:
	block_labels['U'+x[0]] = x[2]

label_font = ImageFont.truetype(font_file, int(label_height))

all_chars = os.listdir('./' + chardir)

plane_one_chars = list()
plane_two_chars = list()
prog1 = re.compile('U[0-9A-F]{4}-.*\.png')
prog2 = re.compile('U[0-9A-F]{5}-.*\.png')

for s in all_chars:
	if prog1.match(s):
		plane_one_chars.append(s)
	elif prog2.match(s):
		plane_two_chars.append(s)

plane_one_chars.sort()
plane_two_chars.sort()
char_list = plane_one_chars + plane_two_chars

page = Image.new('RGB', (page_width, page_height), 0xFFFFFF)
label = ImageDraw.Draw(page)

page_count = 0
page_x = 0
page_y = 0

row_count = 0
col_count = 0

cur_x = margin
cur_y = margin + 3*label_height/5

cur_block = ''
chars_to_print_label = -1

saved_last_page = True
used_labels = set()

num_pages = math.ceil(float(len(char_list))/(rows_per_page * cols_per_page))
num_cells_to_run = int(math.ceil(num_pages/pages_width)*pages_width*rows_per_page*cols_per_page)
char_count = 0

for number in range(num_cells_to_run):
	char_number = col_count + cols_per_page * (page_x + row_count * pages_width) + page_y * (cols_per_page * rows_per_page * pages_width)
	if char_number < len(char_list):
		char = char_list[char_number]
		char_image = Image.open(chardir + char)

		if not cur_block == char[:char.find('-')] and not char[:char.find('-')] in used_labels:
			cur_block = char[:char.find('-')]
			used_labels.add(cur_block)
			chars_to_print_label = 10

		new_width = int(char_width)
		scale = char_width / char_image.size[0]
		new_height = int(scale * char_image.size[1])

		hspacing = 0
		vspacing = char_height - scale * char_image.size[1]

		if new_height > char_height:
			new_height = int(char_height)
			scale = char_width / char_image.size[0]
			new_width = int(scale * char_image.size[0])

			hspacing = char_width - scale * char_image.size[0]
			vspacing = 0

		if chars_to_print_label == 0:
			if cur_block in block_labels:
				label.rectangle((int(cur_x - char_width*10), int(cur_y - 3*label_height/5), int(cur_x), int(cur_y + 2*label_height/5 + label_height/16)), outline='#FFFFFF', fill='#FFFFFF')
				label.text((int(cur_x - char_width*10), int(cur_y - 3*label_height/5)), block_labels[cur_block], font=label_font, fill='#000000')

		char_image = char_image.resize((new_width, new_height), Image.ANTIALIAS)
		page.paste(char_image, (int(cur_x + hspacing/2), int(cur_y + vspacing/2)))

	saved_last_page = False

	cur_x += char_width

	chars_to_print_label -= 1
	char_count += 1
	col_count += 1

	if col_count >= cols_per_page:
		print 'Done with row %d from unicode-page-%.3d-%dx%d-%d.png' %(row_count, page_count, page_width, page_height, cols_per_page)
		print 'Processed %d of %d characters' %(char_count, len(char_list))

		cur_x = margin
		cur_y += char_height + 3*label_height/5

		col_count = 0
		row_count += 1

	if row_count >= rows_per_page:
		print 'Rendering unicode-page-%.3d-%dx%d-%d.png' %(page_count, page_width, page_height, cols_per_page)
		page.save('%sunicode-page-%.3d-%dx%d-%d.png' %(pagedir, page_count, page_width, page_height, cols_per_page))
		saved_last_page = True
		print 'Saved unicode-page-%.3d-%dx%d-%d.png' %(page_count, image_width, image_height, cols_per_page)

		del label
		del page

		page = Image.new('RGB', (page_width, page_height), 0xFFFFFF)
		label = ImageDraw.Draw(page)

		cur_y = margin + 3*label_height/5

		page_count += 1
		row_count = 0
		page_x += 1
		if page_x >= pages_width:
			page_x = 0
			page_y += 1

	
if not saved_last_page:
	print 'Rendering unicode-page-%.3d-%dx%d-%d.png' %(page_count, page_width, page_height, cols_per_page)
	page.save('%sunicode-page-%.3d-%dx%d-%d.png' %(pagedir, page_count, page_width, page_height, cols_per_page))
	print 'Saved unicode-page-%.3d-%dx%d-%d.png' %(page_count, page_width, page_height, cols_per_page)
	print 'Processed %d of %d characters' %(char_count, len(plane_one_chars) + len(plane_two_chars))
	del label
	del page
