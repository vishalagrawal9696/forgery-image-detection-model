"""
Seed SQLite database with initial authentic and manipulated scans for immediate demonstration.
"""
import os
import io
import django
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forgery_system.settings')
django.setup()

from detector.models import ScanRecord
from detector.cnn_engine import analyze_image_forgery

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(BASE_DIR, 'static', 'samples')

def seed_scans():
    print("[SEED] Seeding demo scans into SQLite database...")
    sample_files = [
        'sample_authentic.jpg',
        'sample_spliced_forgery.jpg',
        'sample_ai_portrait.jpg',
        'sample_copy_move.jpg',
    ]

    for fname in sample_files:
        fpath = os.path.join(SAMPLES_DIR, fname)
        if not os.path.exists(fpath):
            continue

        # Check if already seeded
        if ScanRecord.objects.filter(filename=fname).exists():
            print(f"- Already exists in database: {fname}")
            continue

        with open(fpath, 'rb') as f:
            content = f.read()

        img_file = ContentFile(content, name=fname)
        analysis = analyze_image_forgery(img_file)
        
        # Rewind
        img_file.seek(0)
        ela_buffer = io.BytesIO()
        analysis['ela_img'].save(ela_buffer, format='JPEG', quality=95)
        ela_file = ContentFile(ela_buffer.getvalue(), name=f"ela_{fname}")

        record = ScanRecord.objects.create(
            image=img_file,
            ela_image=ela_file,
            filename=fname,
            filesize_kb=round(len(content) / 1024.0, 1),
            dimensions=analysis['dimensions'],
            prediction_label=analysis['prediction_label'],
            is_tampered=analysis['is_tampered'],
            confidence=analysis['confidence'],
            ai_probability=analysis['ai_probability'],
            natural_probability=analysis['natural_probability'],
            processing_time=analysis['processing_time'],
            risk_level=analysis['risk_level'],
            noise_metric=analysis['noise_metric'],
            edge_metric=analysis['edge_metric'],
            texture_metric=analysis['texture_metric'],
            color_metric=analysis['color_metric'],
            forensic_summary=analysis['forensic_summary']
        )
        print(f"[OK] Seeded: {fname} -> {record.prediction_label} ({record.confidence:.1f}%)")

    print(f"[DONE] Total records in SQLite: {ScanRecord.objects.count()}")

if __name__ == '__main__':
    seed_scans()
