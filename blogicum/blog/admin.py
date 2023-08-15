from django.contrib import admin

from .models import Post, Category, Location


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'author', 'category', 'location',
                    'is_published')
    list_filter = ('is_published', 'pub_date', 'category', 'location')
    search_fields = ('title', 'text', 'category__title', 'location__name')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title', 'description')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('name',)
