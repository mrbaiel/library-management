from rest_framework import serializers
from .models import Author, Book, FavoriteBook


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    authors = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Author.objects.all()
    )

    class Meta:
        model = Book
        fields = '__all__'


class BookDetailSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = '__all__'


class FavoriteBookSerializer(serializers.ModelSerializer):
    book_detail = BookDetailSerializer(source='book', read_only=True)

    class Meta:
        model = FavoriteBook
        fields = ('id', 'book', 'book_detail', 'added_at')
        read_only_fields = ('added_at',)