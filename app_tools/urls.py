from django.urls import path
from .views import home, TextSummarizer, SpeedTest, MarkdownToPDFView, PDFToDOCXView,PDFToIMGView,ImagesToPDFView,YouTubeDownloadView

urlpatterns = [
    path('', home.as_view(), name='home'),
    path('summarizer', TextSummarizer.as_view(), name='summarizer'),
    path('speed-check', SpeedTest.as_view(), name='speed-check'),
    path('md2pdf', MarkdownToPDFView.as_view(), name='md2pdf'),
    path('pdf2doc', PDFToDOCXView.as_view(), name='pdf2doc'),
    path('pdf2img', PDFToIMGView.as_view(), name='pdf2img'),
    path('img2pdf', ImagesToPDFView.as_view(), name='img2pdf'),
    path('ytdownloader', YouTubeDownloadView.as_view(), name='ytdownloader'),
]
