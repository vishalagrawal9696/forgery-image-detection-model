from django.contrib import admin
from .models import ScanRecord, ModelBenchmark

@admin.register(ScanRecord)
class ScanRecordAdmin(admin.ModelAdmin):
    list_display = ('filename_display', 'prediction_label', 'confidence', 'risk_level', 'created_at')
    list_filter = ('prediction_label', 'risk_level', 'is_tampered', 'created_at')
    search_fields = ('filename', 'forensic_summary')
    readonly_fields = ('created_at',)

@admin.register(ModelBenchmark)
class ModelBenchmarkAdmin(admin.ModelAdmin):
    list_display = ('metric_name', 'metric_value', 'category', 'updated_at')
    list_filter = ('category',)
