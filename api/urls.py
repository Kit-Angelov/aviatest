from django.urls import path
from .views import *

urlpatterns = [
    path('flights/', Flights),
    path('most/', Most),
    path('diff/', Diff),
]
