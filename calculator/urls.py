from django.urls import path
from . import views

app_name = "calculator"

urlpatterns = [
    path("", views.calculator_view, name="calculator"),
    path("products/", views.CellTypesAPIView.as_view(), name="cell_types_api"),
    path(
        "culture-vessels/",
        views.CultureVesselsAPIView.as_view(),
        name="culture_vessels_api",
    ),
    path("download-excel/", views.DownloadExcelView.as_view(), name="download_excel"),
    path("download-pdf/", views.DownloadPDFView.as_view(), name="download_pdf"),
    path("calculate/", views.CalculateAPIView.as_view(), name="calculate"),
]
