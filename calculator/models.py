from django.db import models


class CellType(models.Model):
    """Model for storing cell type information"""

    product_name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    seeding_density = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        ordering = ["product_name"]

    def __str__(self):
        return f"{self.product_name} ({self.sku})"


class CultureVessel(models.Model):
    """Model for storing culture vessel information"""

    plate_format = models.CharField(max_length=255)
    surface_area_cm2 = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    media_volume_per_well_ml = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "culture_vessels"
        ordering = ["plate_format"]

    def __str__(self):
        return self.plate_format


class CalculationHistory(models.Model):
    """Model for storing calculation history"""

    user = models.ForeignKey(
        "app_users.User", on_delete=models.CASCADE, null=True, blank=True
    )
    suspension_volume = models.DecimalField(max_digits=10, decimal_places=2)
    count1 = models.DecimalField(max_digits=10, decimal_places=2)
    count2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    count3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    viability1 = models.DecimalField(max_digits=5, decimal_places=2)
    viability2 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    viability3 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    cell_type = models.CharField(max_length=255)
    seeding_density = models.DecimalField(max_digits=10, decimal_places=2)
    culture_vessel = models.CharField(max_length=255)
    surface_area = models.DecimalField(max_digits=10, decimal_places=4)
    media_volume = models.DecimalField(max_digits=10, decimal_places=4)
    num_wells = models.IntegerField()
    buffer = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Calculation Histories"

    def __str__(self):
        return f"Calculation by {self.user.email if self.user else 'Anonymous'} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
