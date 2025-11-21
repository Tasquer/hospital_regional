from django.urls import path
from . import views

app_name = "reportes"

urlpatterns = [
    # Dashboard principal
    path("", views.ReportesObstetriciaView.as_view(), name="dashboard_obstetricia"),
    
    # API interna para los gráficos
    path("api/chart-data/", views.ChartDataView.as_view(), name="api_chart_data"),
    
    # Rutas de exportación
    path("exportar/excel/", views.ExportarReporteExcelView.as_view(), name="exportar_excel"),
    path("exportar/pdf/", views.ExportarReportePDFView.as_view(), name="exportar_pdf"),
]