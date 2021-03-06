from django.urls import include, path
from rest_framework import routers

from .views import CustomUserViewSet

router_v1 = routers.DefaultRouter()
router_v1.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),

]
