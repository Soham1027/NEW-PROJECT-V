from django.views import View
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import *
from django.contrib.auth import authenticate,login
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

class ProductCreateView(View):
    def get(self, request):
        form = ProductForm()
        return render(request, 'product_create.html', {'form': form})

    def post(self, request):
        print(request.FILES)
        form = ProductForm(request.POST)

        if form.is_valid():
            # Save the product form to create the product instance
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

        return render(request, 'product_create.html', {'form': form})

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
