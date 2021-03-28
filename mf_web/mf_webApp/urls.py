from django.urls import path
from mf_webApp import views
from mf_webApp.screen.results_screen import ResultScreen

urlpatterns = [
    path('', views.home, name="home"),
    #path('upload', views.upload_image, name="upload"),
    path('result', views.result, name="result"),
    path('list', views.lista, name="list"),
    path('upload',views.lo, name="upload"),
    path('processing',views.processing, name="processing"),
    path('processStress.ajax',views.upImgStress),
    path('processRest.ajax',views.upImgRest),
    path('zona1.ajax',views.zona1, name="zona1"),
    path('zona2.ajax',views.zona2,name="zona2"),
    path('zona3.ajax',views.zona3, name="zona3"),
    path('zona1Imagen.ajax',views.zonaImagen1, name="zona1Imagen"),
    path('zona2Imagen.ajax',views.zonaImagen2, name="zona2Imagen"),
    path('zona3Imagen.ajax',views.zonaImagen3, name="zona3Imagen"),
    path('recargar.ajax',views.recargaImagen, name="recargaImagen"),
    path('movARest.ajax',views.mov_imgAtrasRest, name="mov_imgAtrasRest"),
    path('movDRest.ajax',views.mov_imgDelanteRest, name="mov_imgDelanteRest"),
    path('movAStress.ajax',views.mov_imgAtrasStress, name="mov_imgAtrasStress"),
    path('movDStress.ajax',views.mov_imgDelanteStress, name="mov_imgDelanteStress"),
    path('img_rest.jpg', views.img_rest),
    path('img_stress.png', views.img_stress),
    path('table', views.curve_table, name="table"),
    path('imagerest', views.restlist),
    path('plot.png', views.plot),

]