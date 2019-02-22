from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.99
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipesAPITests(TestCase):
    """Test unauthenticated recipes API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required for retrieving recipes"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipesAPITest(TestCase):
    """Test authorized user recipes API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'user1@gmail.com',
            'password!'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retieve_recipes(self):
        """Test retrieve recipes"""

        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test recipes returned are only for authenicated user"""

        user2 = get_user_model().objects.create_user(
            'user@gmail.com',
            'password!'
        )
        # test_recipe = sample_recipe(user=user2, title='Recipe for user2')
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        # self.assertEqual(res.data[0]['title'], test_recipe.title)
