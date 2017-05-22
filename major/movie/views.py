from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView, View, CreateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy, reverse

from .forms import *
from .models import *

# Create your views here.


class Test(TemplateView):
    template_name = "test.html"


class RegistrationView(View):
    def get(self, request):
        userForm = UserForm()
        context = {
            'userForm': userForm,
        }
        return render(request, 'registration.html', context)

    def post(self, request):
        userForm = UserForm(request.POST or None)
        if userForm.is_valid():
            user = userForm.save(commit=False)
            password = userForm.cleaned_data.get('password2')
            user.set_password(password)
            user.save()

            user = authenticate(username=user.username, password=password)
            messages.success(request, "Registration Successful")
            login(request, user)
            return redirect('movie:test')
        else:
            print(userForm.errors)

        context = {
            'userForm': userForm,
        }
        return render(request, 'registration.html', context)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            messages.warning(request, 'You are already registered.')
            return redirect('movie:test')
        return super(RegistrationView, self).dispatch(request, *args, **kwargs)


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        context = {
            'form': form,
        }
        return render(request, 'login.html', context)

    def post(self, request):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                messages.success(request, "Logged In Successfully")
                login(request, user)
                return redirect('movie:test')
        messages.warning(request, "Log In Failure")
        context = {
            'form': form,
        }
        return render(request, 'login.html', context)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            messages.warning(request, 'You are already logged in.')
            return redirect('movie:test')
        return super(LoginView, self).dispatch(request, *args, **kwargs)


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            logout(request)
        messages.success(request, "Logged Out Successfully")
        return redirect('movie:login')


# class GenreCreateView(View):
#     def get(self, request):
#         form = GenreForm()
#         context = {
#             'form': form,
#         }
#         return render(request, 'genreCreate.html', context)


class GenreCreateView(CreateView):
    model = Genre
    form_class = GenreForm
    template_name = 'genreCreate.html'
    success_url = reverse_lazy("movie:test")

# class ProductCreateView(SuccessMessageMixin, CreateView):
#     model = Product
#     template_name = 'website/productCreate.html'
#     form_class = ProductForm
#     success_url = reverse_lazy("website:productList")
#     success_message = "Product Successfully Added"


# class ProductUpdateView(SuccessMessageMixin, UpdateView):
#     model = Product
#     template_name = 'website/productUpdate.html'
#     form_class = ProductForm
#     success_url = reverse_lazy("website:productList")
#     success_message = "Product Successfully Updated"


# class ProductDetailView(DetailView):
#     model = Product
#     template_name = 'website/productDetail.html'


# class ProductListView(ListView):
#     model = Product
#     template_name = 'website/productList.html'
#     context_object_name = 'products'

#     def get_queryset(self):
#         return Product.objects.filter(deleted_at=None)


# class ProductDeleteView(SuccessMessageMixin, DeleteView):
#     model = Product
#     template_name = 'website/delete.html'
#     success_url = reverse_lazy("website:productList")
#     success_message = "Product Successfully Deleted"
