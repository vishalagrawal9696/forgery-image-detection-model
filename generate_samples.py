import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

samples_dir = os.path.join(os.path.dirname(__file__), 'static', 'samples')
os.makedirs(samples_dir, exist_ok=True)

# 1. Authentic Nature Photo
# Smooth natural landscape with natural organic light diffusion
w, h = 640, 480
img_real = Image.new('RGB', (w, h))
arr_real = np.zeros((h, w, 3), dtype=np.float32)

# Generate smooth natural sky & terrain gradients
for y in range(h):
    for x in range(w):
        # Sky to ground transition
        t = y / h
        if t < 0.55:
            # Sky gradient
            arr_real[y, x, 0] = 120 + 80 * (1 - t*1.8)
            arr_real[y, x, 1] = 160 + 50 * (1 - t*1.8)
            arr_real[y, x, 2] = 230 - 30 * t
        else:
            # Rolling green hills
            arr_real[y, x, 0] = 50 + 20 * np.sin(x / 50.0)
            arr_real[y, x, 1] = 110 + 30 * np.cos(x / 60.0) - 20 * (t - 0.55)
            arr_real[y, x, 2] = 45 + 15 * np.sin(x / 80.0)

# Soft Gaussian filter for continuous natural lens diffusion
img_real = Image.fromarray(np.clip(arr_real, 0, 255).astype(np.uint8))
img_real = img_real.filter(ImageFilter.GaussianBlur(radius=1.5))
# Natural uniform camera compression
img_real.save(os.path.join(samples_dir, 'sample_authentic.jpg'), 'JPEG', quality=95)



# 2. Spliced Forged Image
# Background saved at low quality (Q=75), then foreign object pasted and saved at high quality (Q=98)
img_bg = Image.new('RGB', (w, h), (200, 220, 240))
d_bg = ImageDraw.Draw(img_bg)
d_bg.rectangle([0, 280, w, h], fill=(60, 120, 60)) # grass field
# Save background at Q=75
bg_path = os.path.join(samples_dir, '_temp_bg.jpg')
img_bg.save(bg_path, 'JPEG', quality=75)
img_bg_loaded = Image.open(bg_path).convert('RGB')

# Create foreign object (red sports vehicle / alien artifact)
obj = Image.new('RGB', (180, 120), (220, 30, 40))
d_obj = ImageDraw.Draw(obj)
d_obj.ellipse([20, 30, 160, 100], fill=(240, 180, 30))
d_obj.rectangle([40, 50, 140, 90], fill=(10, 20, 40))
# Splice into background without uniform noise
img_bg_loaded.paste(obj, (220, 220))
# Re-save at Q=96 (causes sharp ELA compression mismatch at boundaries)
img_bg_loaded.save(os.path.join(samples_dir, 'sample_spliced_forgery.jpg'), 'JPEG', quality=96)
if os.path.exists(bg_path):
    os.remove(bg_path)


# 3. AI Synthetic Portrait (similar to colorful cubist portrait in screenshot!)
img_ai = Image.new('RGB', (512, 512), (18, 22, 34))
d_ai = ImageDraw.Draw(img_ai)
# Draw complex cubist geometric color mosaic
colors = [
    (240, 90, 40), (255, 175, 45), (35, 140, 225), (150, 45, 200),
    (220, 40, 80), (30, 190, 160), (255, 215, 0), (60, 70, 90),
    (230, 120, 70), (45, 95, 180), (180, 70, 150), (255, 160, 120)
]
np.random.seed(42)
for i in range(120):
    x1 = np.random.randint(40, 470)
    y1 = np.random.randint(40, 470)
    box_w = np.random.randint(30, 90)
    box_h = np.random.randint(30, 90)
    col = colors[i % len(colors)]
    d_ai.rectangle([x1, y1, min(x1 + box_w, 510), min(y1 + box_h, 510)], fill=col)

# Add stylized face outlines
d_ai.ellipse([160, 100, 350, 380], outline=(20, 20, 25), width=6)
d_ai.line([(190, 220), (240, 200), (290, 220)], fill=(10, 10, 20), width=5)
d_ai.line([(250, 200), (230, 280), (270, 290)], fill=(10, 10, 20), width=5)
d_ai.line([(210, 330), (250, 340), (290, 330)], fill=(200, 30, 50), width=6)
# Glasses frame
d_ai.rectangle([180, 180, 240, 230], outline=(10, 10, 15), width=4)
d_ai.rectangle([260, 180, 320, 230], outline=(10, 10, 15), width=4)
d_ai.line([(240, 205), (260, 205)], fill=(10, 10, 15), width=4)

img_ai.save(os.path.join(samples_dir, 'sample_ai_portrait.jpg'), 'JPEG', quality=95)


# 4. Copy-Move Forgery
# Image where a patch from the same image is duplicated elsewhere (classic copy-move attack)
img_cm = Image.new('RGB', (600, 400), (50, 120, 180))
d_cm = ImageDraw.Draw(img_cm)
# Draw trees and meadow
d_cm.rectangle([0, 220, 600, 400], fill=(40, 110, 50))
# Original tree
d_cm.ellipse([100, 120, 200, 260], fill=(30, 80, 35))
d_cm.rectangle([140, 240, 160, 300], fill=(90, 55, 30))
# Crop tree and copy-move to the right
tree_crop = img_cm.crop((95, 115, 205, 305))
img_cm.paste(tree_crop, (360, 115))
# Re-save with edge blur on second tree
img_cm.save(os.path.join(samples_dir, 'sample_copy_move.jpg'), 'JPEG', quality=94)

print("Created 4 sample images in static/samples/")
