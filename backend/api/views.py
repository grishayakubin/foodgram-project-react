from datetime import datetime as dt
from urllib.parse import unquote

from django.contrib.auth import get_user_model
from django.db.models import F, Sum, Q
from django.http.response import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Ingredient, IngredientContained, Recipe, Tag
from .permissions import IsAdminOrReadOnly, IsAuthorStaffOrReadOnly
from .paginator import PageNumberPagination
from .mixins import AddDelViewMixin
from .serializers import (
    IngredientSerializer, RecipeSerializer,
    ShortRecipeSerializer, TagSerializer,
    UserSubscribeSerializer
)

User = get_user_model()

class UserViewSet(DjoserUserViewSet, AddDelViewMixin):
    pagination_class = PageNumberPagination
    add_serializer = UserSubscribeSerializer

    @action(methods=('GET', 'POST', 'DELETE',), detail=True)
    def subscribe(self, request, id):
        return self.add_remove_relation(id, 'follow_M2M')

    @action(methods=('get',), detail=False)
    def subscriptions(self, request):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)
        
        authors = user.follow.all()
        pages = self.paginate_queryset(authors)
        serializer = UserSubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        name = self.request.query_params.get('name')
        queryset = self.queryset
        if name:
            if name[0] == '%':
                name = unquote(name)
            name = name.lower()
            stw_queryset = list(queryset.filter(name__startswith=name))
            cnt_queryset = queryset.filter(name__contains=name)
            stw_queryset.extend(
                [i for i in cnt_queryset if i not in stw_queryset]
            )
            queryset = stw_queryset
        return queryset


class RecipeViewSet(ModelViewSet, AddDelViewMixin):
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorStaffOrReadOnly,)
    pagination_class = PageNumberPagination
    add_serializer = ShortRecipeSerializer

    def get_queryset(self):
        queryset = self.queryset

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        user = self.request.user
        if user.is_authenticated:
            is_in_shopping = self.request.query_params.get('is_in_shopping_cart')
            if is_in_shopping in ('1', 'true'):
                queryset = queryset.filter(is_in_shopping_list=user.id)
            elif is_in_shopping in ('0', 'false'):
                queryset = queryset.exclude(is_in_shopping_list=user.id)

            is_favorited = self.request.query_params.get('is_favorited')
            if is_favorited in ('1', 'true'):
                queryset = queryset.filter(is_favorite=user.id)
            if is_favorited in ('0', 'false'):
                queryset = queryset.exclude(is_favorite=user.id)

        return queryset

    @action(methods=('GET', 'POST', 'DELETE',), detail=True)
    def favorite(self, request, pk):
        return self.add_remove_relation(pk, 'is_favorite_M2M')

    @action(methods=('GET', 'POST', 'DELETE',), detail=True)
    def shopping_cart(self, request, pk):
        return self.add_remove_relation(pk, 'shopping_cart_M2M')

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        TIME_FORMAT = '%d/%m/%Y %H:%M'
        user = self.request.user
        if not user.shopping_list.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        ingredients = IngredientContained.objects.filter(
            recipe__in=(user.shopping_list.values('id'))
        ).values(
            ingredient=F('ingredients__name'),
            measure=F('ingredients__measurement_unit')
        ).annotate(amount=Sum('amount'))

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = (
            f'Список покупок для пользователя {user.first_name}:\n\n'
        )
        for ing in ingredients:
            shopping_list += (
                f'{ing["ingredient"]}: {ing["amount"]} {ing["measure"]}\n'
            )

        shopping_list += (
            f'\nДата составления {dt.now().strftime(TIME_FORMAT)}.\n\n'
            'Made in Foodgram 2022 (c)'
        )

        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
