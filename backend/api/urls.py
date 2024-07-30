from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from .views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                    FoodgramUserViewSet, short_url_redirect)

router_v1 = DefaultRouter()
router_v1.register(r'users', FoodgramUserViewSet, basename='users')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    re_path(
        r'^(?P<surl>\w+)', short_url_redirect, name='short_url_redirect'),
]
