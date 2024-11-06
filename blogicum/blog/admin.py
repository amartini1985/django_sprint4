from django.contrib import admin

from .models import Location, Post, Category


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'category',
        'location'
    )
    list_editable = (
        'is_published',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)
    empty_value_display = 'Не задано'


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'title',
    )


admin.site.register(Location)
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
