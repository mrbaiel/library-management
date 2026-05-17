from django.shortcuts import render

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Author, Book, FavoriteBook
from .serializers import AuthorSerializer, BookSerializer, BookDetailSerializer, FavoriteBookSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    filterset_fields = ['genre', 'authors', 'publication_date']
    search_fields = ['title', 'authors__last_name']
    ordering_fields = ['publication_date', 'authors__last_name', 'genre']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return BookDetailSerializer
        return BookSerializer


class FavoriteBookViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = FavoriteBookSerializer

    def get_queryset(self):
        return FavoriteBook.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)