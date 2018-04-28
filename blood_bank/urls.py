from django.urls import path

from blood_bank import webhook, views

urlpatterns = [
    path('', views.index, name='index'),
    path('29c32786-8ab8-456e-8d89-516fc124164c-e024b70d-fb0f-47e8-a0ec-9ab3db722fcb',
         webhook.index, name='webhook'),
    path('logs', views.error_log, name='error_log'),
    path('data', views.data_dump, name='data_dump'),
]
