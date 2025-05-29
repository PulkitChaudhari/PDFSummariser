from django.contrib import admin
from django.urls import path
from core.views import home, handle_decision

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('decision/', handle_decision, name='handle_decision'),
]
