"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework.authtoken.views import obtain_auth_token

from app.views import RestaurantView, MenuView, EmployeeView, CurrentDayMenuView

urlpatterns = [
    path(r'admin/i18n/', include('django.conf.urls.i18n')),
    path(r'admin/', admin.site.urls),
    path(r'api/token/', obtain_auth_token, name='token'),
    path(r'api/restaurant/', RestaurantView.as_view({'post': 'create'}), name='restaurant'),
    path(r'api/menu/<int:pk>/', MenuView.as_view({'post': 'create', 'get': 'retrieve'}), name='menu'),
    path(r'api/current-day-menu/', CurrentDayMenuView.as_view({'get': 'retrieve'}), name='current_day_menu'),
    path(r'api/current-day-menu/vote/', CurrentDayMenuView.as_view({'put': 'vote'}), name='current_day_menu_vote'),
    path(r'api/current-day-menu/result/', CurrentDayMenuView.as_view({'get': 'result'}), name='current_day_menu_result'),
    path(r'api/employee/<int:pk>/', EmployeeView.as_view({'post': 'create'}), name='employee'),
]
