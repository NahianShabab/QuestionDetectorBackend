from PIL import Image

# Load image
img = Image.open(r"pngimg.com - Footprints_PNG16.png").convert("RGBA")
pixels = img.load()

# Define the color you want to set (R, G, B)
new_color = (255, 0, 0)  # red

width, height = img.size
for x in range(width):
    for y in range(height):
        r, g, b, a = pixels[x, y]
        if a != 0:  # non-transparent pixel
            pixels[x, y] = (*new_color, 255)
        else:       # fully transparent
            pixels[x, y] = (0, 0, 0, 0)

# Save result
img.save("output.png")
