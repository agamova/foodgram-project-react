from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import exceptions, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Follow, User
from recipes.serializers import SubscribeUserSerializer


SUBSCRIBE_ERR_MSG = 'Нельзя подписаться дважды или на самого себя!'
UNSUBSCRIBE_ERR_MSG = 'Вы не были подписаны!'


class CustomUserViewSet(UserViewSet):
    @action(detail=False, methods=['get', ],
            permission_classes=[permissions.IsAuthenticated],
            serializer_class=SubscribeUserSerializer)
    def subscriptions(self, request):
        follower_objects = request.user.follower.all()
        followers = []
        for object in follower_objects:
            followers.append(object.following)
        page = self.paginate_queryset(followers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'delete'],
            permission_classes=[permissions.IsAuthenticated],
            serializer_class=SubscribeUserSerializer)
    def subscribe(self, request, id):
        user = request.user
        following = get_object_or_404(User, pk=id)
        already_subscribed = Follow.objects.filter(
            user=user,
            following=following
        ).exists()
        if request.method == 'GET':
            if already_subscribed or user == following:
                raise exceptions.ValidationError(SUBSCRIBE_ERR_MSG)
            Follow.objects.create(user=user, following=following)
            serializer = self.get_serializer(following)
            return Response(serializer.data)
        else:
            if not already_subscribed:
                raise exceptions.ValidationError(UNSUBSCRIBE_ERR_MSG)
            follow = Follow.objects.get(user=user, following=following)
            follow.delete()
            return Response(status=204)



