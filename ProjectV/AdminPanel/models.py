import uuid
from django.db import models

# Create your models here.
from django.utils.timezone import now

import os
from uuid import uuid4
from django.db import models
from django.core.validators import MinValueValidator

def product_image_upload_path(instance, filename):
    """
    Generate a file path for a new product image in the format:
    /media/product_images/{product_id}_{unique_id}.jpg
    """
    ext = filename.split('.')[-1]  # Get the file extension
    unique_id = uuid.uuid4().hex[:8]  # Generate an 8-character unique ID
    filename = f"{instance.product.id}_{unique_id}.{ext}"
    return os.path.join("product_images", filename)
class Product(models.Model):
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
    product_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(max_length=500, blank=True, null=True)
    
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.IntegerField(choices=ITEM_SIZE_CHOICES, blank=True, null=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    item_discount = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], default=0.00)
    
    item_view = models.PositiveIntegerField(default=0)
    recently_viewed = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        details = f"{self.product_name}"
        if self.color:
            details += f" - {self.color}"
        if self.size:
            details += f" - {dict(self.ITEM_SIZE_CHOICES).get(self.size)}"
        return details

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ['-item_view', '-recently_viewed']
        db_table = 'products'


class ProductImages(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=product_image_upload_path)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Image of {self.product.product_name}"
    
    class Meta:
        verbose_name_plural = 'Product Images'
        ordering = ['-created_at']
        db_table = 'product_images'

class ProductLike(models.Model):
 

    created_by_id = models.IntegerField(default=0)  

    products = models.ForeignKey(Product, related_name='likes', on_delete=models.CASCADE)
    date_liked = models.DateTimeField(default=now)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True) 

    class Meta:
        db_table = 'product_like'
        unique_together = ('created_by_id','products')  # Ensure one like per user/team/group per post



# class ProductVariant(models.Model):
#     ITEM_SIZE_CHOICES = [
#         (1, 'Extra Small'),
#         (2, 'Small'),
#         (3, 'Medium'),
#         (4, 'Large'),
#         (5, 'XL'),
#         (6, 'XXL'),
#         (7, 'XXXL'),
#     ]

#     id = models.AutoField(primary_key=True)
#     product = models.ForeignKey(ProductItem, related_name='variants', on_delete=models.CASCADE)
#     color = models.CharField(max_length=50)
#     size = models.IntegerField(choices=ITEM_SIZE_CHOICES)
#     quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])

#     item_discount = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], default=0.00)
#     created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
#     updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)

#     def __str__(self):
#         return f"{self.product.product_name} - {self.color} - {dict(self.ITEM_SIZE_CHOICES).get(self.size)}"

#     class Meta:
#         verbose_name_plural = 'Product Variants'
#         ordering = ['product', 'color', 'size']
#         db_table = 'product_variants'