from django.urls import path
from .views import home,TextSummarizer,SpeedTest
urlpatterns = [
    path('', home.as_view(), name='home'),
    path('summarizer', TextSummarizer.as_view(), name='summarizer'),
    path('speed-check', SpeedTest.as_view(), name='speed-check'),
]