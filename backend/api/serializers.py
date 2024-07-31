from django.db.transaction import atomic

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import (User, Subscription)


class UserSignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'password']


class UserGetSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and Subscription.objects.filter(user=request.user, author=obj
                                            ).exists())


class UserSubscribtionGetSerializer(UserGetSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = UserGetSerializer.Meta.fields + ['recipes', 'recipes_count']
        read_only_fields = fields

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass
        return RecipeSmallSerializer(recipes, many=True,
                                     context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['user', 'author']
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request.user == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return UserSubscribtionGetSerializer(
            instance.author, context={'request': request}
        ).data


class AvatarSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ['avatar']

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class TagSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientGetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='ingredient.id',
        read_only=True
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class IngredientPostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeSmallSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerialiser(
        many=True,
        read_only=True
    )
    author = UserGetSerializer(
        read_only=True
    )
    ingredients = IngredientGetSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(
        required=True
    )

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and Favorite.objects.filter(
                user=request.user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user, recipe=obj).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientPostSerializer(
        many=True,
        source='recipe_ingredients',
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        allow_null=False,
    )
    image = Base64ImageField(
        required=True
    )

    class Meta:
        model = Recipe
        fields = ['ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time']

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле image - пустое')
        return value

    def validate(self, data):
        if data.get('recipe_ingredients') is None:
            raise serializers.ValidationError(
                'Не переданно поля ingredients')
        if data.get('tags') is None:
            raise serializers.ValidationError(
                'Не переданно поля tags')
        ingredients_list = []
        tags_list = []
        for ingredient in data.get('recipe_ingredients'):
            ingredients_list.append(ingredient.get('ingredient').id)
        if not ingredients_list:
            raise serializers.ValidationError(
                'Вы пытаетесь добавить рецепт без ингредиентов'
            )
        if len(set(ingredients_list)) != len(ingredients_list):
            raise serializers.ValidationError(
                'Вы пытаетесь добавить в рецепт '
                'несколько одинаковых ингредиентов'
            )
        for tag in data.get('tags'):
            tags_list.append(tag)
        if not tags_list:
            raise serializers.ValidationError(
                'Вы пытаетесь добавить рецепт без тега'
            )
        if len(set(tags_list)) != len(tags_list):
            raise serializers.ValidationError(
                'Вы пытаетесь добавить в рецепт несколько одинаковых тегов'
            )
        return data

    @staticmethod
    def create_ingredients(ingredients, recipe):
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient.get('ingredient').id
            amount = ingredient.get('amount')
            ingredient_list.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient_id,
                    amount=amount
                )
            )
        RecipeIngredient.objects.bulk_create(ingredient_list)

    @atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', [])
        tags_data = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', [])
        tags_data = validated_data.pop('tags', [])
        instance = super().update(instance, validated_data)
        instance.tags.set(tags_data)
        instance.ingredients.clear()
        self.create_ingredients(ingredients_data, instance)
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeGetSerializer(
            instance,
            context={'request': request}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['user', 'recipe']
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSmallSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже есть в списке покупок'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSmallSerializer(
            instance.recipe,
            context={'request': request}
        ).data
