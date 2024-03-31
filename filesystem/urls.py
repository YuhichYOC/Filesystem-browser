from django.urls import path

from . import views

app_name = 'filesystem'
urlpatterns = [
    path('', views.browse, name='index'),
]
