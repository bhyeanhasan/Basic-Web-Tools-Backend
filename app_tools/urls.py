from .views import home, MarkdownToPDFView, PDFToDOCXView, PDFToIMGView, ImagesToPDFView, \
    YouTubeDownloadView, BarcodeView, QRCodeView
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Basic Tools API",
        default_version='v1',
        description="API for some basic tools",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="noyon@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', home.as_view(), name='home'),
    # path('summarizer', TextSummarizer.as_view(), name='summarizer'),
    # path('speed-check', SpeedTest.as_view(), name='speed-check'),
    path('md2pdf', MarkdownToPDFView.as_view(), name='md2pdf'),
    path('pdf2doc', PDFToDOCXView.as_view(), name='pdf2doc'),
    path('pdf2img', PDFToIMGView.as_view(), name='pdf2img'),
    path('img2pdf', ImagesToPDFView.as_view(), name='img2pdf'),
    path('ytdownloader', YouTubeDownloadView.as_view(), name='ytdownloader'),
    path('barcode', BarcodeView.as_view(), name='barcode'),
    path('qrcode', QRCodeView.as_view(), name='qrcode'),

    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

