from django.contrib import admin

from .models import Photo, PhotoCategory, PhotoTag


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
admin.site.register(PhotoCategory, PhotoCategoryAdmin)
admin.site.register(PhotoTag, TagAdmin)
