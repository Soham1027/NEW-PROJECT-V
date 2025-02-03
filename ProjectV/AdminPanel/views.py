from django.views import View
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import *
from django.contrib.auth import authenticate,login
# Create your views here.
class LoginUser(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

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
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Replace 'dashboard' with your desired path
        
        return render(request, 'product_create.html', {'form': form})
    

class ProductVariantCreateView(View):
    def get(self, request):
        form = ProductVariantForm()
        return render(request, 'product_variant_create.html', {'form': form})
    
    def post(self, request):
        form = ProductVariantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Replace 'dashboard' with your desired path
        
        return render(request, 'product_variant_create.html', {'form': form})