from django.contrib import admin
from django.urls import path,include
from StudApp import views

urlpatterns = [
    path('',views.index),
]