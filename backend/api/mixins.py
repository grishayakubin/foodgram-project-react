from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED)

class AddDelViewMixin:

    add_serializer = None

    def add_remove_relation(self, obj_id, manager):
        assert self.add_serializer is not None, (
            f'{self.__class__.__name__} should include '
            'an `add_serializer` attribute.'
        )

        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)

        managers = {
            'follow_M2M': user.follow,
            'is_favorite_M2M': user.favorites,
            'shopping_cart_M2M': user.shopping_list,
        }
        manager = managers.get(manager)

        if not manager:
            return Response(status=HTTP_400_BAD_REQUEST)

        obj = get_object_or_404(self.queryset, id=obj_id)
        serializer = self.add_serializer(
            obj, context={'request': self.request}
        )
        
        if self.request.method in ('GET', 'POST'):
            if manager.filter(id=obj_id).exists():
                return Response(serializer.data)
            manager.add(obj)
            return Response(serializer.data, status=HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if manager.filter(id=obj_id).exists():
                manager.remove(obj)
                return Response(status=HTTP_204_NO_CONTENT)
        
        return Response(status=HTTP_400_BAD_REQUEST)
