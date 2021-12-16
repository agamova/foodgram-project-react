from django.urls import include, path
from rest_framework import routers

from .views import CustomUserViewSet


router = routers.DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),

]
