from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import CellType, CultureVessel
import json
import decimal
from decimal import Decimal
from .utils import validate_required_fields, perform_calculation


@login_required
def calculator_view(request):
    """Main calculator view"""
    from bitbio.countries import COUNTRIES

    return render(request, "calculator/calculator.html", {"countries": COUNTRIES})


@method_decorator(csrf_exempt, name="dispatch")
class CellTypesAPIView(View):
    """API endpoint for cell types"""

    def get(self, request):
        try:
            cell_types = list(
                CellType.objects.values("id", "product_name", "sku", "seeding_density")
            )
            return JsonResponse(cell_types, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class CultureVesselsAPIView(View):
    """API endpoint for culture vessels"""

    def get(self, request):
        try:
            vessels = list(
                CultureVessel.objects.values(
                    "id", "plate_format", "surface_area_cm2", "media_volume_per_well_ml"
                )
            )
            return JsonResponse(vessels, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class DownloadExcelView(View):
    """Handle Excel download"""

    def post(self, request):
        try:
            data = json.loads(request.body)

            # Extract data from request
            result_data = {
                "cellDensity": data.get("cellDensity", ""),
                "cellsPerWell": data.get("cellsPerWell", ""),
                "requiredCells": data.get("requiredCells", ""),
                "volumeToDilute": data.get("volumeToDilute", ""),
                "volumeToSeed": data.get("volumeToSeed", ""),
                "volumePerWell": data.get("volumePerWell", ""),
                "wellCount": data.get("wellCount", ""),
                "suspensionVolume": data.get("suspensionVolume", ""),
                "liveCellCount": data.get("liveCellCount", ""),
                "cellViability": data.get("cellViability", ""),
                "cellType": data.get("cellType", ""),
                "seedingDensity": data.get("seedingDensity", ""),
                "cultureVessel": data.get("cultureVessel", ""),
                "surfaceArea": data.get("surfaceArea", ""),
                "mediaVolume": data.get("mediaVolume", ""),
                "buffer": data.get("buffer", ""),
                "timezone": data.get("timezone", "UTC"),
                "count1": data.get("count1", ""),
                "count2": data.get("count2", ""),
                "count3": data.get("count3", ""),
                "viability1": data.get("viability1", ""),
                "viability2": data.get("viability2", ""),
                "viability3": data.get("viability3", ""),
            }

            # For now, return success response
            # In a real implementation, you would generate and return an Excel file
            return JsonResponse(
                {
                    "success": True,
                    "message": "Excel download functionality will be implemented here",
                    "data": result_data,
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class DownloadPDFView(View):
    """Handle PDF download"""

    def post(self, request):
        try:
            data = json.loads(request.body)

            # Extract data from request
            result_data = {
                "suspensionVolume": data.get("suspensionVolume", ""),
                "count1": data.get("count1", ""),
                "count2": data.get("count2", ""),
                "count3": data.get("count3", ""),
                "viability1": data.get("viability1", ""),
                "viability2": data.get("viability2", ""),
                "viability3": data.get("viability3", ""),
                "cellType": data.get("cellType", ""),
                "seedingDensity": data.get("seedingDensity", ""),
                "cultureVessel": data.get("cultureVessel", ""),
                "surfaceArea": data.get("surfaceArea", ""),
                "mediaVolume": data.get("mediaVolume", ""),
                "wellCount": data.get("wellCount", ""),
                "buffer": data.get("buffer", ""),
                "volumeToDilute": data.get("volumeToDilute", ""),
                "volumeToSeed": data.get("volumeToSeed", ""),
                "cellDensity": data.get("cellDensity", ""),
                "requiredCells": data.get("requiredCells", ""),
                "cellsPerWell": data.get("cellsPerWell", ""),
                "volumePerWell": data.get("volumePerWell", ""),
                "timezone": data.get("timezone", "UTC"),
                "warnings": data.get("warnings", ""),
            }

            # For now, return success response
            # In a real implementation, you would generate and return a PDF file
            return JsonResponse(
                {
                    "success": True,
                    "message": "PDF download functionality will be implemented here",
                    "data": result_data,
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class CalculateAPIView(View):
    """Server-side calculation endpoint to mirror client-side calculator.js logic"""

    def post(self, request):
        try:
            payload = json.loads(request.body or b"{}")

            validation = validate_required_fields(payload)
            if validation.has_errors:
                return JsonResponse(
                    {
                        "success": False,
                        "validation": {
                            "missingFields": validation.missing_fields,
                            "negativeValueFields": validation.negative_value_fields,
                            "percentageOverLimitFields": validation.percentage_over_limit_fields,
                        },
                    },
                    status=400,
                )

            result = perform_calculation(payload)
            if "error" in result:
                return JsonResponse(
                    {"success": False, "message": result["error"]}, status=400
                )

            return JsonResponse({"success": True, "result": result})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)
