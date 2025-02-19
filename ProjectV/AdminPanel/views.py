from django.views import View
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from .forms import *
from django.contrib.auth import authenticate,login
from django.http import JsonResponse
from VApp.models import *

# Create your views here.
class AdminLoginUser(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)

            if user is not None:
                if user.is_superuser:
                    login(request, user)
              
                    return redirect('dashboard')  # Replace 'dashboard' with your desired path
                else:
                    return redirect('login')  # Replace 'dashboard' with your desired path

            else:
                messages.error(request, "Invalid username or password.")
        
        return render(request, 'login.html', {'form': form})

class Home(View):
    def get(self, request):
        return render(request, 'index.html')

def get_subcategories(request):
    category_id = request.GET.get('category_id')
    
    if category_id:
        category = get_object_or_404(ProductCategory, id=category_id)
        subcategories = SubCategory.objects.filter(category=category)
    else:
        subcategories = SubCategory.objects.all()

    subcategories_data = subcategories.values('id', 'sub_category_name')
    return JsonResponse(list(subcategories_data), safe=False)
class ProductCreateView(View):
    def get(self, request):
        form = ProductForm()
     
        return render(request, 'product_create.html', {'form': form})

    def post(self, request):
        print(request.FILES)
        form = ProductForm(request.POST)
      

        if form.is_valid():
            product = form.save()
        

            # Handle multiple image uploads
            images = request.FILES.getlist('images[]')  # Get the list of image files
            default_images = request.POST.getlist('default_image[]')  # Get the list of default image checkboxes

            print(images)
            print(default_images)

            # Check if there are any selected default images
            default_image_set = False
            
            for i, image in enumerate(images):
                is_default = i == 0 and not default_images  # Set the first image as default if no checkbox is checked
                if default_images and str(i) in default_images:
                    is_default = True

                # Create a new ProductImages instance and associate it with the product
                ProductImages.objects.create(
                    product=product,
                    image=image,
                    is_default=is_default  # Mark it as the default image if applicable
                )

                if is_default:
                    default_image_set = True

            # Redirect to the desired path if the form was valid
            return redirect('dashboard')  # Redirect to the desired path

        # Print form errors for debugging
        print(form.errors)

        return render(request, 'product_create.html',  {'form': form})

class ProductCategoryCreateView(View):
    def get(self, request):
        form = ProductCategoryForm()
        return render(request, 'product_category.html', {'form': form})
    
    def post(self, request):
        form = ProductCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Ensure 'dashboard' is a valid URL name
        
        return render(request, 'product_category.html', {'form': form})

class SubCategoryCreateView(View):
    def get(self, request):
        form = SubCategoryForm()
        return render(request, 'sub_category.html', {'form': form})

    def post(self, request):
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect to relevant page
        
        return render(request, 'sub_category.html', {'form': form})



class ProductPercentageView(View):
    def get(self, request):
        form = ProductDiscountForm()
        return render(request, 'product_discount.html', {'form': form})

    def post(self, request):
        form = ProductDiscountForm(request.POST)
        if form.is_valid():
            # Save a discount for each selected product
            discount_percentage = form.cleaned_data['discount_percentage']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            products = form.cleaned_data['product']  # This will be a list of selected products

            # Create a discount for each selected product
            for product in products:
                ProductDiscount.objects.create(
                    product=product,
                    discount_percentage=discount_percentage,
                    start_date=start_date,
                    end_date=end_date
                )
            
            return redirect('dashboard')  # Replace 'dashboard' with your desired path
        
        return render(request, 'product_discount.html', {'form': form})

# class ProductVariantCreateView(View):
#     def get(self, request):
#         form = ProductVariantForm()
#         return render(request, 'product_variant_create.html', {'form': form})
    
#     def post(self, request):
#         form = ProductVariantForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('dashboard')  # Replace 'dashboard' with your desired path
        
#         return render(request, 'product_variant_create.html', {'form': form})
