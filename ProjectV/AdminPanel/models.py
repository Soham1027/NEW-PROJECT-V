import uuid
from django.db import models

# Create your models here.
from django.utils.timezone import now

import os
from uuid import uuid4
from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator

def product_image_upload_path(instance, filename):
    """
    Generate a file path for a new product image in the format:
    /media/product_images/{product_id}_{unique_id}.jpg
    """
    ext = filename.split('.')[-1]  # Get the file extension
    unique_id = uuid.uuid4().hex[:8]  # Generate an 8-character unique ID
    if instance.product_variants:
        filename = f"{instance.product_variants.id}_{unique_id}.{ext}"
    else:
        filename = f"{instance.product.id}_{unique_id}.{ext}"
    return os.path.join("product_images", filename)

class ProductCategory(models.Model):
    id = models.AutoField(primary_key=True)
    # product = models.ForeignKey(Product, related_name='categories', on_delete=models.CASCADE)
    category_name = models.CharField(max_length=100, unique=True)  # Make category names unique

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = 'Product Categories'
        ordering = ['category_name']
        db_table = 'product_categories'


class SubCategory(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(ProductCategory, related_name='subcategories', on_delete=models.CASCADE)
    sub_category_name = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sub_category_name}"

    class Meta:
        verbose_name_plural = 'Subcategories'
        ordering = ['sub_category_name']
        db_table = 'sub_categories'
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

    SHOES_SIZE_CHOICES = [
        (1, '6'),
        (2, '7'),
        (3, '8'),
        (4, '9'),
        (5, '10'),
        (6, '11'),
        (7, '12'),
    ]
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('All', 'All'),
    ]

    id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(max_length=500, blank=True, null=True)
    
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.IntegerField(choices=ITEM_SIZE_CHOICES, blank=True, null=True)
    shoes_size = models.IntegerField(choices=SHOES_SIZE_CHOICES, blank=True, null=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
 
    category = models.ForeignKey(ProductCategory, related_name='products', on_delete=models.CASCADE,blank=True, null=True)
    subcategory = models.ForeignKey(SubCategory, related_name='subproducts', on_delete=models.CASCADE, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    
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

class ProductDiscount(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='discounts', on_delete=models.CASCADE)
    discount_percentage = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    def __str__(self):
        return f"{self.product.product_name} - {self.discount_percentage}% Off"
    
    class Meta:
        verbose_name_plural = 'Product Discounts'
        ordering = ['-start_date', '-end_date']
        db_table = 'product_discounts'


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
    SHOES_SIZE_CHOICES = [
        (1, '6'),
        (2, '7'),
        (3, '8'),
        (4, '9'),
        (5, '10'),
        (6, '11'),
        (7, '12'),
    ]

    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE,blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.IntegerField(choices=ITEM_SIZE_CHOICES,blank=True, null=True)
    shoes_size = models.IntegerField(choices=SHOES_SIZE_CHOICES, blank=True, null=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])

 
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)

    def __str__(self):
        return f"{self.product.product_name} - {self.color} - {dict(self.ITEM_SIZE_CHOICES).get(self.size)}"

    class Meta:
        verbose_name_plural = 'Product Variants'
        ordering = ['product', 'color', 'size']
        db_table = 'product_variants'


class ProductImages(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE,blank=True, null=True )
    product_variants= models.ForeignKey(ProductVariant, related_name='images', on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to=product_image_upload_path,blank=True, null=True)
    variant_image= models.ImageField(upload_to=product_image_upload_path,blank=True, null=True)
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



class ProductSerach(models.Model):
    id = models.AutoField(primary_key=True)
    search = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.search
    
    class Meta:
        verbose_name_plural = 'Product Searches'
        ordering = ['-created_at']
        db_table = 'product_searches'
        