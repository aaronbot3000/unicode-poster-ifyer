from urllib import urlopen
from PIL import Image
import re, os

def getPixelValue(image_data, coord):
	pixel = image_data[coord]
	pixel_data = pixel[0]
	pixel_data += pixel[1]
	pixel_data += pixel[2]
	return pixel_data

def isHorizontalLine(image_data, bound, linestart, sensitivity):
	for vx in range(linestart[0], min(linestart[0] + 120, bound)):
		pixel_data = getPixelValue(image_data, (vx, linestart[1]))
		if pixel_data >= sensitivity:
			return False
	return True

def isVerticalLine(image_data, bound, linestart, sensitivity):
	for vy in range(linestart[1], min(linestart[1] + 200, bound)):
		pixel_data = getPixelValue(image_data, (linestart[0], vy))
		if pixel_data >= sensitivity:
			return False
	return True

def findTable(image_data, size):
	sensitivity = 20
	cornerX = -1
	cornerY = -1
	tableBeginX = -1
	tableBeginY = -1
	tableWidth = -1
	linesearchwidth = 10
# find top corner of the table
	for y in range(200, 800):
		for x in range(200, 1000):
			pixel_data = getPixelValue(image_data, (x,y))
			foundLine = False
			if pixel_data < sensitivity and isVerticalLine(image_data, size[1], (x,y), sensitivity) and isHorizontalLine(image_data, size[0], (x,y), sensitivity):
				foundLine = True
				cornerX = x
				cornerY = y
				break
		if foundLine:
			break
	if not foundLine:
		return None

	columns = list()
	rows = list()
# find the other side of the x line
	for vx in range(cornerX, size[0]):
		pixel_data = getPixelValue(image_data, (vx, cornerY + linesearchwidth))
		if pixel_data >= sensitivity:
			tableBeginX = vx
			break

# find the other side of the y line
	for vy in range(cornerY, size[1]):
		pixel_data = getPixelValue(image_data, (cornerX + linesearchwidth, vy))
		if pixel_data >= sensitivity:
			tableBeginY = vy
			break

	col_begin = tableBeginX
	vx = tableBeginX
	row_begin = tableBeginY
	vy = tableBeginY

# Find the rest of the columns
	while vx < size[0]:
		pixel_data = getPixelValue(image_data, (vx, tableBeginY))
		if pixel_data < sensitivity and isVerticalLine(image_data, size[1], (vx, tableBeginY), sensitivity):
			columns.append((col_begin, vx))
			print 'Column at %d to %d'%(col_begin, vx)
# Go around the line
			for vx2 in range(vx, size[0]):
				pixel_data = getPixelValue(image_data, (vx2, tableBeginY))
				if pixel_data >= sensitivity:
					col_begin = vx2
					break
			vx = vx2
		else:
			vx += 1

# Find the rest of the rows
	while vy < size[1]:
		pixel_data = getPixelValue(image_data, (tableBeginX, vy))
		if pixel_data < sensitivity and isHorizontalLine(image_data, size[0], (tableBeginX, vy), sensitivity):
			rows.append((row_begin, vy))
			print 'Row at %d to %d'%(row_begin, vy)
# Go around the line
			for vy2 in range(vy, size[1]):
				pixel_data = getPixelValue(image_data, (tableBeginX, vy2))
				if pixel_data >= sensitivity:
					row_begin = vy2
					break
			vy = vy2
		else:
			vy += 1

	return (rows, columns)

def findAllRows(image_data, bounds):
	trans_count = 0
	rows = list()
	for y in range(bounds[1], bounds[3]):
		hitBlack = False
		for x in range(bounds[0], bounds[2]):
			if getPixelValue(image_data, (x, y)) < 600:
				hitBlack = True
				if trans_count == 0:
					rows.append(y)
					trans_count = 1
				if trans_count == 2:
					trans_count = 3
				break
		if not hitBlack:
			if trans_count == 1:
				trans_count = 2
			if trans_count == 3:
				trans_count = 0
	return rows

# Variables
pageURL = 'http://www.unicode.org/charts/PDF/'
pageURL52 = 'http://www.unicode.org/charts/PDF/Unicode-5.2/'
pdfdir = '../pdf_files/'
pngdir = '../png_files/'
chardir = '../char_files/'
if not os.path.isdir(pdfdir):
	os.mkdir(pdfdir)
if not os.path.isdir(pngdir):
	os.mkdir(pngdir)
if not os.path.isdir(chardir):
	os.mkdir(chardir)

# special case for block U3400
case_U3400 = list()
# label offset from cell corner
case_U3400.append((16, 100))
# column offset from cell corner
case_U3400.append((160, 299))

# special case for block U4E00
case_U4E00 = list()
# label offset from cell corner
case_U4E00.append((16, 100))
# column offset from cell corner
case_U4E00.append((154, 284))

# special case for block UFB50 page 04
# These columns are inserted between the second last and last columns
case_UFB50 = list()
case_UFB50.append((1869, 2000))
case_UFB50.append((2001, 2132))

# special case for block UFFF0 page 2
# These rows are inserted at the end
case_UFFF0 = list()
case_UFFF0.append((2696, 2860))
case_UFFF0.append((2861, 3025))

webpage = urlopen(pageURL).read()
results = re.findall('U1?[0-9A-F]{4}.pdf', webpage)

pdffiles = set()
for result in results:
	pdffiles.add(result)

existing_pdf_files = set(os.listdir('./' + pdfdir))
existing_png_files = os.listdir('./' + pngdir)
for e in pdffiles:
	if e not in existing_pdf_files:
		print 'Downloading %s'%e
		f = file(pdfdir + e, 'w')
		if e == 'UF900.pdf':
			f.write(urlopen(pageURL52 + 'U52-F900.pdf').read())
		else:
			f.write(urlopen(pageURL + '%s' % e).read())
		f.close()
	else:
		print 'Already downloaded %s'%e

for e in pdffiles:
	needConversion = True
	for fname in existing_png_files:
		if fname[:fname.find('-')] == e[:e.rfind('.')]:
			needConversion = False
			break

	if needConversion:
		print 'Converting %s to png'%e
		os.system('pdftoppm -q -r %d -png %s%s %s%s' %(300, pdfdir, e, pngdir, e[:e.rfind('.')]))
	else:
		print 'Already converted %s to png'%e


page_count = 1
existing_char_files = set([i[:i.rfind('-')] for i in os.listdir('./' + chardir)])
all_pages = os.listdir('./' + pngdir)

for pngfile in all_pages:
# See if there is a character file that came from this page
	if pngfile[:pngfile.rfind('.')] in existing_char_files:
		print 'Already considered %s (%d/%d)' %(pngfile, page_count, len(all_pages))
		page_count += 1
		continue

	print 'Considering %s (%d/%d)' %(pngfile, page_count, len(all_pages))
	page_count += 1
	page = Image.open(pngdir + pngfile)
	page_data = page.load()
	cells = findTable(page_data, page.size)

	if cells is not None:
# Check for special cases
		if pngfile[:pngfile.find('-')] == 'U3400':
			print 'Special case block U3400'
			charCount = 0
			for col in cells[1]: 
				rows = findAllRows(page_data, (col[0] + case_U3400[0][0], cells[0][0][0], col[0] + case_U3400[0][1], cells[0][0][1]))
				for row in rows:
# Bounds for CJK character
					lbound = col[0] + case_U3400[1][0]
					rbound = col[0] + case_U3400[1][1]
					tbound = row - 13
					bbound = row + 124

# Extract character and save it
					bounds = (lbound, tbound, rbound, bbound)
					letter = page.crop(bounds)

					print 'Saving %s%s-%.4d.png' %(chardir,pngfile[:pngfile.rfind('.')], charCount)
					letter.save(chardir + '%s-%.4d.png' %(pngfile[:pngfile.rfind('.')], charCount))
					charCount += 1
			continue

		if pngfile[:pngfile.find('-')] == 'U4E00':
			print 'Special case block U4E00'
			charCount = 0
			for col in cells[1]: 
				rows = findAllRows(page_data, (col[0] + case_U4E00[0][0], cells[0][1][0], col[0] + case_U4E00[0][1], cells[0][1][1]))
				for row in rows:
# Bounds for CJK character
					lbound = col[0] + case_U4E00[1][0]
					rbound = col[0] + case_U4E00[1][1]
					tbound = row - 13
					bbound = row + 124
					
# Extract character and save it
					bounds = (lbound, tbound, rbound, bbound)
					letter = page.crop(bounds)

					print 'Saving %s%s-%.4d.png' %(chardir,pngfile[:pngfile.rfind('.')], charCount)
					letter.save(chardir + '%s-%.4d.png' %(pngfile[:pngfile.rfind('.')], charCount))
					charCount += 1
			continue

# Special case UFB50 with filled in boxes
		if pngfile[:pngfile.rfind('.')] == 'UFB50-04':
			print 'Special case block UFB50 page 4'
			new_cols = cells[1]
			new_cols = new_cols[:len(new_cols) - 1] + case_UFB50 + new_cols[len(new_cols)-1:len(new_cols)]
			cells = (cells[0], new_cols)

# Special case UFFF0 with filled in boxes
		if pngfile[:pngfile.rfind('.')] == 'UFFF0-2':
			print 'Special case block UFFF0 page 2'
			new_rows = cells[0]
			new_rows = new_rows + case_UFFF0
			cells = (new_rows, cells[1])


# Not special case 
		charCount = 0
		for col in cells[1]:
			for row in cells[0]:

# Extract character and save it
				bounds = (col[0], row[0]+2, col[1], row[1])
				letter = page.crop(bounds)
				letter.load()
				print 'Saving %s%s-%.4d.png' %(chardir,pngfile[:pngfile.rfind('.')], charCount)
				letter.save(chardir + '%s-%.4d.png' %(pngfile[:pngfile.rfind('.')], charCount))
				charCount += 1
	else:
		f = file('%s%s-0000.empty'%(chardir,pngfile[:pngfile.rfind('.')]), 'w')
		f.write('This file has been processed!\n')
		f.close()
		print 'No table'

print 'Done'
