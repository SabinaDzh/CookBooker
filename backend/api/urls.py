from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       FoodgramUserViewSet)
from api.short_url import short_url_redirect

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('users', FoodgramUserViewSet, basename='users')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('s/<str:short_url>/', short_url_redirect, name='short_url_redirect'),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
