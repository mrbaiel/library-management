from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, BookViewSet, FavoriteBookViewSet

router = DefaultRouter()
router.register('authors', AuthorViewSet, basename='author')
router.register('books', BookViewSet, basename='book')
router.register('favorites', FavoriteBookViewSet, basename='favorite')


urlpatterns = [
    path('', include(router.urls)),
]