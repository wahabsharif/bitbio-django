from django.contrib import admin
from .models import CellType, CultureVessel, CalculationHistory


@admin.register(CellType)
class CellTypeAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'sku', 'seeding_density', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product_name', 'sku')
    ordering = ('product_name',)


@admin.register(CultureVessel)
class CultureVesselAdmin(admin.ModelAdmin):
    list_display = ('plate_format', 'surface_area_cm2', 'media_volume_per_well_ml', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('plate_format',)
    ordering = ('plate_format',)


@admin.register(CalculationHistory)
class CalculationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'cell_type', 'culture_vessel', 'num_wells', 'created_at')
    list_filter = ('created_at', 'cell_type', 'culture_vessel')
    search_fields = ('user__email', 'cell_type', 'culture_vessel')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
