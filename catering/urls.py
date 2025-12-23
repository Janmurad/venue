from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DishViewSet, SaladViewSet, WeddingMenuViewSet

router = DefaultRouter()
router.register(r'dishes', DishViewSet, basename='dish')
router.register(r'salads', SaladViewSet, basename='salad')
router.register(r'menus', WeddingMenuViewSet, basename='menu')

app_name = 'catering'

urlpatterns = [
    path('', include(router.urls)),
]