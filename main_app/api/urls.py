from django.urls import path, include
from rest_framework.routers import SimpleRouter

from main_app.api import views

# Create a SimpleRouter instance to automatically generate routes for viewsets
router = SimpleRouter()
router.register(r'scheduler', views.SchedulerPanelViewSet, basename='scheduler')
router.register(r'booker', views.BookerPanelViewSet, basename='booker')
router.register(r'admin', views.AdminPanelViewSet, basename='admin')

urlpatterns = [
    # ---------- API routes for Scheduler, Booker, and Admin panels ----------
    path('', include(router.urls)),
]



