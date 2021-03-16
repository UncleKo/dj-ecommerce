from django.contrib import admin

from .models import Photo, Category, Tag


class PhotoAdmin(admin.ModelAdmin):
    filter_horizontal = ("tags",)


class PhotoInline(admin.StackedInline):
    model = Photo.tags.through
    extra = 1


class PhotoCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']


class TagAdmin(admin.ModelAdmin):
    inlines = [PhotoInline]


admin.site.register(Photo, PhotoAdmin)
admin.site.register(Category, PhotoCategoryAdmin)
admin.site.register(Tag, TagAdmin)
