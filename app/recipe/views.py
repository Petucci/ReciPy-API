from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Ingredient, Recipe
from recipe import serializers


class BaseRecipeAttributeViewSet(
                viewsets.GenericViewSet, 
                mixins.CreateModelMixin,
                mixins.ListModelMixin):
    """Base class for extension"""

    authentication_classes = {TokenAuthentication,}
    permission_classes = {IsAuthenticated,}
    
    def get_queryset(self):
        """Return objects for the current authenticated user only"""

        return self.queryset.filter(user=self.request.user).order_by('name')

    def perform_create(self, serializer):
        """Create a new tag"""

        serializer.save(user = self.request.user)

class TagViewSet(BaseRecipeAttributeViewSet):
    """Manage tags in the database"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

class IngredientViewSet(BaseRecipeAttributeViewSet):
    """Viewset for the ingredients model"""

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset for the recipe model"""

    authentication_classes = {TokenAuthentication,}
    permission_classes = {IsAuthenticated,}

    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """Retrieve the recipe for the authenticated user"""

        return self.queryset.filter(user = self.request.user).order_by('id')

    def perform_create(self, serializer):
        """Creates an recipe with current authenticated user"""
        serializer.save(user = self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        
        return self.serializer_class