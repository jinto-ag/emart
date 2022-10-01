from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model

from core.models import (
    Address,
    Cart,
    CartItem,
    Feedback,
    Order,
    Profile,
    ReviewModel,
    WishlistModel,
)

USER = get_user_model()


class CustomUserCreationForm(auth_forms.UserCreationForm):
    class Meta:
        model = USER
        fields = ["username", "email"]


# Profile form
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = (
            "status",
            "location",
            "address",
            "user",
            "is_loyal",
            "is_active",
            "account_type",
        )


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = (
            "location",
            "status",
            "created_on",
            "updated_on",
        )


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        exclude = ("is_replied", "status", "user")


class CartItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CartItemForm, self).__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance and instance.id:
            self.fields["product"].widget = forms.HiddenInput(attrs={})

    class Meta:
        model = CartItem
        fields = ["product", "quantity"]

    def clean_product(self):
        instance = getattr(self, "instance", None)
        if instance:
            return instance.product
        else:
            return self.cleaned_data.get("product", None)


CartItemFormSet = forms.modelformset_factory(
    CartItem, form=CartItemForm, edit_only=True, extra=0, can_delete=True
)

AddressFormSet = forms.modelformset_factory(
    Address, form=AddressForm, edit_only=True, extra=1, can_delete=False
)


class BillingAddressForm(AddressForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Billing Address"
        self.prefix = "billing"


class ShippingAddressForm(AddressForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Shipping Address"
        self.prefix = "shipping"


class CurrencyForm(forms.Form):
    INR = Order.CurrencyChoices.INR
    DOLLAR = Order.CurrencyChoices.DOLLAR
    CURRENCY_CHOICES = (
        (INR, "Indian Rupee"),
        (DOLLAR, "Dollar"),
    )
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES, label="")


# Wishlist form
class WishlistForm(forms.ModelForm):
    class Meta:
        model = WishlistModel
        fields = ["name", "description"]


class AddToWishlistForm(forms.ModelForm):
    class Meta:
        model = WishlistModel
        fields = ["name"]


AddToWishlistFormSet = forms.modelformset_factory(
    WishlistModel, form=AddToWishlistForm, edit_only=True, extra=0, can_delete=True
)

# Product Review form
class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewModel
        fields = ["rating", "comment"]
