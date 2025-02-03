from django.db import models

# Create your models here.

import os
from uuid import uuid4
from django.db import models
from django.core.validators import MinValueValidator

def user_directory_path(instance, filename):
    content_type = 'images' if instance.content_type == 1 else 'videos'
    ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid4()}{ext}"
    return f'media/{content_type}/{unique_filename}'

class ProductItem(models.Model):
    id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(max_length=500, blank=True, null=True)
    item_view = models.PositiveIntegerField(default=0)
    item_like = models.PositiveIntegerField(default=0)
    recently_viewed = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name_plural = 'Product Items'
        ordering = ['-item_view', '-item_like', '-recently_viewed']
        db_table = 'product_items'


class ProductVariant(models.Model):
    ITEM_SIZE_CHOICES = [
        (1, 'Extra Small'),
        (2, 'Small'),
        (3, 'Medium'),
        (4, 'Large'),
        (5, 'XL'),
        (6, 'XXL'),
        (7, 'XXXL'),
    ]

    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(ProductItem, related_name='variants', on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    size = models.IntegerField(choices=ITEM_SIZE_CHOICES)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    image_file = models.FileField(upload_to=user_directory_path, blank=True, null=True)
    video_story_file = models.FileField(upload_to=user_directory_path, blank=True, null=True)
    item_discount = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], default=0.00)

    def __str__(self):
        return f"{self.product.product_name} - {self.color} - {dict(self.ITEM_SIZE_CHOICES).get(self.size)}"
