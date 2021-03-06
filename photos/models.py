from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill, ResizeToFit
from core.models import Item


class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name="タグ")

    class Meta:
        verbose_name_plural = 'タグ'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="カテゴリー")

    class Meta:
        verbose_name_plural = 'カテゴリー'

    def __str__(self):
        return self.name


class Photo(models.Model):

    origin = models.ImageField(upload_to="other_images/", verbose_name="画像")

    large = ImageSpecField(source="origin",
                           processors=[ResizeToFit(1920, 1920)],
                           format='JPEG',
                           options={'quality': 80}
                           )

    medium = ImageSpecField(source='origin',
                            processors=[ResizeToFit(700, 700)],
                            format="JPEG",
                            options={'quality': 80}
                            )

    small = ImageSpecField(source='origin',
                           processors=[ResizeToFill(250, 250)],
                           format="JPEG",
                           options={'quality': 80}
                           )

    thumb = ImageSpecField(source='origin',
                           processors=[ResizeToFill(100, 100)],
                           format="JPEG",
                           options={'quality': 80}
                           )

    date_posted = models.DateTimeField(default=timezone.now)

    author = models.ForeignKey(
        User, null=True, on_delete=models.CASCADE, related_name="photos")

    private = models.BooleanField(default=False, verbose_name="非公開にする")

    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name="posts", null=True, blank=True, verbose_name="カテゴリー(option)")

    tags = models.ManyToManyField(
        Tag, blank=True, related_name="posts", verbose_name="タグ(option)")

    item = models.ForeignKey(Item, on_delete=models.CASCADE,
                             related_name="other_images", null=True, blank=True, verbose_name="商品")

    order = models.IntegerField(verbose_name="順番", default=99)

    # 編集後そのidのページに戻る

    def get_absolute_url(self):
        return reverse('photo-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.origin.url
