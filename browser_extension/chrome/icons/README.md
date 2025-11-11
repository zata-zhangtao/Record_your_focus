# Extension Icons

This directory should contain the following icon files:

- `icon16.png` - 16x16 pixels (toolbar icon)
- `icon48.png` - 48x48 pixels (extension management page)
- `icon128.png` - 128x128 pixels (Chrome Web Store, installation)

## Creating Icons

You can create icons using:

1. **Design Tools**: Figma, Sketch, Photoshop, GIMP
2. **Icon Generators**: Various online tools
3. **SVG to PNG Conversion**: Use SVG and convert to different sizes

## Icon Guidelines

- Use a simple, recognizable design
- Include good contrast for visibility
- Consider both light and dark backgrounds
- Match the app's branding and purpose

## Temporary Placeholder

Until proper icons are created, you can use simple placeholder icons. Here's a quick way to generate them:

### Using ImageMagick (Linux/macOS)

```bash
# Install ImageMagick if needed
# sudo apt-get install imagemagick  # Ubuntu/Debian
# brew install imagemagick          # macOS

# Create simple circular icons with camera/recording symbol
convert -size 16x16 xc:transparent -fill "#4CAF50" -draw "circle 8,8 8,2" icon16.png
convert -size 48x48 xc:transparent -fill "#4CAF50" -draw "circle 24,24 24,6" icon48.png
convert -size 128x128 xc:transparent -fill "#4CAF50" -draw "circle 64,64 64,16" icon128.png
```

### Using Python + Pillow

```python
from PIL import Image, ImageDraw

def create_icon(size, filename):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw circle
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin],
                 fill='#4CAF50', outline='#45a049', width=2)

    # Draw center dot (recording indicator)
    center = size // 2
    dot_radius = size // 6
    draw.ellipse([center-dot_radius, center-dot_radius,
                  center+dot_radius, center+dot_radius],
                 fill='white')

    img.save(filename, 'PNG')

create_icon(16, 'icon16.png')
create_icon(48, 'icon48.png')
create_icon(128, 'icon128.png')
```

For now, the extension will load with default Chrome icons until custom icons are added.
