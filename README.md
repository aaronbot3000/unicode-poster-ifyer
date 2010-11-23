# Unicode Posterifyer
# About:
These python scripts go to the Unicode website, scrapes the pdfs of the Basic and Supplementary Multilingual Plane, converts them to png images, extracts the characters, and rearrange them into poster form, with block labels.

# Prerequisites:
- Python (I have 2.6)
- Python Imaging Library
- pdftoppm

# To use:
Run download-rasterize.py. It will download, convert, and split the unicode set into images of individual characters. It can detect for the most part where it left off if it is stopped, but try not to kill it in the middle of writing an image.
Run combine-characters.py. It has the ability to print the poster such that it forms a grid x sheets of paper across and y sheets of paper down, or just one giant poster. The arguments are the width and height of each page in pixels, the width in pages (For a poster 10 pages across, this number is 10. For a single sheet poster, this number is 1), characters per line, and margin from the characters to the edges of the page. 

## Example
./download-rasterize.py
./combine-characters.py 3300 2550 12 32 0

The above downloads and rasterizes the pdf files, then combines the characters into a poster where each page is 3300 by 2550 pixels (making the picture approximately 300dpi on US letter in landscape), the total poster size is 12 sheets wide (it becomes around 10 sheets tall), there are 32 characters per page, and there is a 0 pixel margin.
