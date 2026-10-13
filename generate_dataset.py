"""
Dataset Generation Script for Forgery Image Detection
Generates paired authentic and manipulated/forged image datasets for training and evaluation.
"""
import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')

def create_synthetic_dataset(num_train=80, num_test=20):
    splits = {
        'train': num_train,
        'test': num_test
    }

    random.seed(42)
    np.random.seed(42)

    for split, count in splits.items():
        auth_dir = os.path.join(DATASET_DIR, split, 'authentic')
        forg_dir = os.path.join(DATASET_DIR, split, 'forged')
        os.makedirs(auth_dir, exist_ok=True)
        os.makedirs(forg_dir, exist_ok=True)

        print(f"Generating {split} dataset ({count} authentic, {count} forged)...")

        for i in range(count):
            # Base dimensions
            w, h = 256, 256
            
            # Generate random realistic scene (Authentic)
            # Organic sky + ground + landscape shapes
            base_col_r = random.randint(80, 160)
            base_col_g = random.randint(120, 200)
            base_col_b = random.randint(140, 230)
            img = Image.new('RGB', (w, h), (base_col_r, base_col_g, base_col_b))
            draw = ImageDraw.Draw(img)

            # Draw hills/landscape
            hill_col = (random.randint(40, 90), random.randint(80, 140), random.randint(40, 80))
            draw.polygon([(0, h), (random.randint(60, 120), random.randint(100, 180)), (w, h)], fill=hill_col)
            draw.polygon([(random.randint(100, 180), h), (random.randint(180, 240), random.randint(90, 150)), (w, h)], fill=(hill_col[0]+20, hill_col[1]+15, hill_col[2]+10))

            # Add sun or structures
            sun_x = random.randint(30, 150)
            sun_y = random.randint(20, 80)
            sun_r = random.randint(30, 60)
            draw.ellipse([sun_x, sun_y, sun_x + sun_r, sun_y + sun_r], fill=(255, random.randint(220, 250), random.randint(150, 200)))

            # Apply consistent camera sensor noise (PRNU)
            arr = np.array(img).astype(np.float32)
            noise = np.random.normal(0, random.uniform(3.0, 5.0), arr.shape)
            arr_noisy = np.clip(arr + noise, 0, 255).astype(np.uint8)
            authentic_img = Image.fromarray(arr_noisy)

            # Single uniform JPEG compression pass
            auth_path = os.path.join(auth_dir, f"auth_{i+1:04d}.jpg")
            authentic_img.save(auth_path, 'JPEG', quality=random.randint(88, 95))

            # Now create forged counterpart (Splicing, Copy-Move, or Local Filtering)
            forged_img = authentic_img.copy()
            forgery_type = random.choice(['splice', 'copy_move', 'local_blur'])

            if forgery_type == 'splice':
                # Splice foreign object with discordant compression
                splice_w = random.randint(40, 90)
                splice_h = random.randint(40, 90)
                foreign = Image.new('RGB', (splice_w, splice_h), (random.randint(200, 255), random.randint(20, 70), random.randint(20, 70)))
                d_f = ImageDraw.Draw(foreign)
                d_f.ellipse([10, 10, splice_w-10, splice_h-10], fill=(random.randint(20, 50), random.randint(150, 250), random.randint(200, 255)))
                
                pos_x = random.randint(20, w - splice_w - 20)
                pos_y = random.randint(20, h - splice_h - 20)
                forged_img.paste(foreign, (pos_x, pos_y))

            elif forgery_type == 'copy_move':
                # Copy patch from one location to another
                patch_w = random.randint(35, 75)
                patch_h = random.randint(35, 75)
                src_x = random.randint(10, w - patch_w - 50)
                src_y = random.randint(10, h - patch_h - 50)
                patch = forged_img.crop((src_x, src_y, src_x + patch_w, src_y + patch_h))
                
                dst_x = min(src_x + random.randint(40, 100), w - patch_w)
                dst_y = min(src_y + random.randint(20, 60), h - patch_h)
                forged_img.paste(patch, (dst_x, dst_y))

            else:
                # Local inpainting / blurring anomaly
                patch_x = random.randint(30, w - 80)
                patch_y = random.randint(30, h - 80)
                crop_patch = forged_img.crop((patch_x, patch_y, patch_x + 60, patch_y + 60))
                blurred_patch = crop_patch.filter(ImageFilter.GaussianBlur(radius=random.uniform(4.0, 7.0)))
                forged_img.paste(blurred_patch, (patch_x, patch_y))

            # Save forged image with recompression (creating ELA discrepancies)
            forg_path = os.path.join(forg_dir, f"forged_{i+1:04d}.jpg")
            forged_img.save(forg_path, 'JPEG', quality=95)

    print(f"Dataset generation complete in {DATASET_DIR}")

if __name__ == '__main__':
    create_synthetic_dataset()
