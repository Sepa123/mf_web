from django.urls import path
from mf_webApp import views

urlpatterns = [
    path('', views.home, name="home"),
    path('upload', views.upload_image, name="upload"),
    path('result', views.result, name="result"),
    path('list', views.lista, name="list"),
    path('upl',views.lo, name="upload"),
    path('process.ajax',views.ajax_server),
    path('process2.ajax',views.ajax_server2),
]