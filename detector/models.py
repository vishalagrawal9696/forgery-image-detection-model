import os
from django.db import models

class ScanRecord(models.Model):
    VERDICT_CHOICES = [
        ('Authentic / Real Natural', 'Authentic / Real Natural'),
        ('Manipulated / Forged', 'Manipulated / Forged'),
        ('AI-Generated Content', 'AI-Generated Content'),
    ]
    RISK_CHOICES = [
        ('LOW', 'Low Risk'),
        ('MODERATE', 'Moderate Risk'),
        ('HIGH', 'High Risk'),
    ]

    image = models.ImageField(upload_to='scans/original/%Y/%m/%d/')
    ela_image = models.ImageField(upload_to='scans/ela/%Y/%m/%d/', blank=True, null=True)
    filename = models.CharField(max_length=255)
    filesize_kb = models.FloatField(default=0.0)
    dimensions = models.CharField(max_length=50, default="")
    
    # CNN Model Predictions
    prediction_label = models.CharField(max_length=100, choices=VERDICT_CHOICES)
    is_tampered = models.BooleanField(default=False)
    confidence = models.FloatField(default=95.0)  # percentage 0-100
    ai_probability = models.FloatField(default=5.0)  # percentage 0-100
    natural_probability = models.FloatField(default=95.0)
    
    # Forensic Metrics
    processing_time = models.FloatField(default=2.1)  # in seconds
    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES, default='LOW')
    noise_metric = models.FloatField(default=0.15)
    edge_metric = models.FloatField(default=0.18)
    texture_metric = models.FloatField(default=0.12)
    color_metric = models.FloatField(default=0.14)
    
    # Detailed Automated Analysis
    forensic_summary = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.filename} - {self.prediction_label} ({self.confidence:.1f}%)"

    @property
    def filename_display(self):
        return os.path.basename(self.filename)


class ModelBenchmark(models.Model):
    metric_name = models.CharField(max_length=100)
    metric_value = models.CharField(max_length=50)
    category = models.CharField(max_length=50)  # 'Accuracy', 'Performance', 'Comparison'
    description = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.metric_name}: {self.metric_value}"
