from django.http import FileResponse
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthenticatedAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeGetSerializer,
                             ShoppingCartSerializer, TagSerialiser,
                             AvatarSerializer, UserSubscribeSerializer,
                             UserSubscribtionGetSerializer)
from api.utils import create_shopping_list
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class FoodgramUserViewSet(UserViewSet):
    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(detail=True,
            methods=['put'],
            permission_classes=[IsAuthenticated])
    def avatar(self, request, id=None):
        serializer = AvatarSerializer(
            request.user,
            data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request, id=None):
        user = request.user
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        serializer = UserSubscribeSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        deleted, _ = Subscription.objects.filter(
            user=request.user, author=author).delete()
        if deleted == 0:
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            subscription__user=request.user)
        page = self.paginate_queryset(subscriptions)
        serializer = UserSubscribtionGetSerializer(
            page, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerialiser
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def create_recipe_user_instance(self, request, serializer, instance):
        serializer = serializer(
            data={'user': request.user.id, 'recipe': instance.id, },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe_user_instance(
            self,
            request,
            model,
            error_message,
            instance):
        deleted, _ = model.objects.filter(
            user=request.user, recipe=instance).delete()
        if deleted == 0:
            return Response({'errors': error_message},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        if self.kwargs.get('pk'):
            filter_kwargs = {'pk': self.kwargs['pk']}
        elif self.kwargs.get('short_url'):
            filter_kwargs = {'short_url': self.kwargs['short_url']}
        else:
            return super().get_object()
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = request.build_absolute_uri(f'/{recipe.short_url}')

        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        return self.create_recipe_user_instance(
            request=request,
            serializer=FavoriteSerializer,
            instance=get_object_or_404(Recipe, id=pk))

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.delete_recipe_user_instance(
            request=request,
            model=Favorite,
            error_message='У вас нет этого рецепта в избранном',
            instance=get_object_or_404(Recipe, id=pk))

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        return self.create_recipe_user_instance(
            request=request,
            serializer=ShoppingCartSerializer,
            instance=get_object_or_404(Recipe, id=pk))

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.delete_recipe_user_instance(
            request=request,
            model=ShoppingCart,
            error_message='У вас нет этого рецепта в списке покупок',
            instance=get_object_or_404(Recipe, id=pk))

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcarts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        return FileResponse(create_shopping_list(ingredients),
                            as_attachment=True,
                            filename='shopping_list.txt')
