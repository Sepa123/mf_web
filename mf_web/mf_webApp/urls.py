from django.urls import path
from mf_webApp import views
from mf_webApp.screen.results_screen import ResultScreen

urlpatterns = [
    path('', views.home, name="home"),
    path('upload', views.upload_image, name="upload"),
    path('result', views.result, name="result"),
    path('list', views.lista, name="list"),
    path('upl',views.lo, name="upload"),
    path('processing',views.processing, name="processing"),
    path('processStress.ajax',views.upImgStress),
    path('processRest.ajax',views.upImgRest),
    #path('processData.ajax',views.send_data),
    path('plot/', views.plot),

]