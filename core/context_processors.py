from django.core.paginator import Paginator
from django.contrib.auth import forms as auth_forms
from core.forms import CustomUserCreationForm, FeedbackForm
from django.conf import settings

from core.models import ProductModel, Cart


def common_data(request):
    products = ProductModel.objects.filter(status=True)
    cart = None
    if request.user.is_authenticated:
        cart = Cart.get_cart(request)
    context = {
        "reCAPTCHA_site_key": settings.GOOGLE_RECAPTCHA_SITE_KEY,
        "project_name": "Emart",
        "page_name": "page name",
        "products": products,
        "cart": cart,
        "login_form": auth_forms.AuthenticationForm(),
        "signup_form": CustomUserCreationForm(),
        "contact_form": FeedbackForm(),
    }
    return context
