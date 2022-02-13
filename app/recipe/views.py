from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
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

        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )

        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(user=self.request.user).order_by('name').distinct()

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

    def _params_to_ints(self, query_string):
        """Convert query string to list of integers"""
        return [int(str_id) for str_id in query_string.split(',')]


    def get_queryset(self):
        """Retrieve the recipe for the authenticated user"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')

        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)


        return queryset.filter(user = self.request.user).order_by('id')

    def perform_create(self, serializer):
        """Creates an recipe with current authenticated user"""
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        
        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to an recipe"""

        recipe = self.get_object()

        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )