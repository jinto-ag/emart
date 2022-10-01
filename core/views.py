import json

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.contrib.auth import mixins as auth_mixins
from django.contrib.auth import views as auth_views
from django.core.mail import send_mail
from django.db.models import F, Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic as views

import core.payment as payment
from core.forms import (
    AddressForm,
    AddToWishlistForm,
    AddToWishlistFormSet,
    BillingAddressForm,
    CartItemFormSet,
    CurrencyForm,
    CustomUserCreationForm,
    FeedbackForm,
    ProductReviewForm,
    ProfileForm,
    ShippingAddressForm,
    WishlistForm,
)
from core.models import (
    Address,
    Cart,
    CartItem,
    CategoryModel,
    Feedback,
    Order,
    Payment,
    ProductModel,
    Profile,
    WishlistModel,
)

# ================================================ #
# Global Variables                                 #
# ================================================ #
USER = get_user_model()
RAZORPAY_CLIENT = payment.get_client()


# ================================================ #
# General views                                    #
# ================================================ #


# Home view
class HomeView(views.TemplateView):
    template_name = "core/home.html"


# About view
class AboutView(views.TemplateView):
    template_name = "core/about.html"


# Contact view
class ContactView(views.View):
    template_name = "core/contact.html"
    form_class = FeedbackForm

    def get(self, request):
        context = {
            "form": self.form_class(),
        }

        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        data = form.cleaned_data
        name = data.get("name")
        subject = "Thanks for your valuable feedback"
        to_email = data.get("email")
        message = data.get("message")
        from_email = settings.EMAIL_HOST_USER
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[
                    to_email,
                ],
            )
            form.save()
            messages.success(self.request, "Thanks for your valuable feedback!")

        except:
            messages.error(self.request, "Can not send feedback! Please try again!")
        return redirect(reverse_lazy("core:contact"))

    def form_invalid(self, form):
        return render(self.request, self.template_name, {"form": form})


# News view
class NewsView(views.TemplateView):
    template_name = "core/news.html"


# Shop view
class ShopView(views.ListView):
    template_name = "core/shop.html"
    model = ProductModel
    paginate_by = 5
    context_object_name = "products"


# ================================================ #
# User Related views                               #
# ================================================ #
# Profile view
class ProfileView(auth_mixins.LoginRequiredMixin, views.View):
    template_name = "core/profile.html"
    profile_model = Profile
    address_model = Address
    profile_form_class = ProfileForm
    address_form_class = AddressForm

    def get(self, request):

        profile = self.profile_model.get_obj(request)
        address = self.address_model.get_obj_for_profile(request)

        context = {
            "profile": profile,
            "address_form": self.address_form_class(instance=address),
            "profile_form": self.profile_form_class(instance=profile),
        }

        return render(request, self.template_name, context)

    def post(self, request):
        profile = self.profile_model.get_obj(request)
        address = self.address_model.get_obj_for_profile(request)

        profile_form = self.profile_form_class(
            request.POST, request.FILES, instance=profile
        )

        address_form = self.address_form_class(request.POST, instance=address)
        if profile_form.is_valid() and address_form.is_valid():
            return self.form_valid(profile_form, address_form)
        return self.form_invalid(profile_form, address_form)

    def form_valid(self, profile_form, address_form):
        user = self.request.user

        address = address_form.save()
        profile = self.profile_model.get_obj(self.request)

        if not hasattr(profile, "user"):
            profile_form.instance.user = user

        if not hasattr(profile, "address"):
            profile_form.instance.address = address

        profile_form.save()
        messages.success(self.request, "Profile updated successfully!")
        url = self.request.META.get("HTTP_REFERER")
        return redirect(url)

    def form_invalid(self, profile_form):
        messages.error(self.request, "Profile failed to updated!")
        return render(self.request, self.template_name, {"profile_form": profile_form})


# Dashboard view
class DashboardView(auth_mixins.LoginRequiredMixin, views.View):
    template_name = "core/dashboard.html"

    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        user = self.request.user
        cart = Cart.get_cart(self.request)
        orders = Order.objects.filter(cart__user=user)
        payments = Payment.objects.filter(order__cart__user=user)

        context = {
            "cart": cart,
            "orders": orders,
            "payments": payments,
        }
        context.update(kwargs)
        return context


# settings view
class SettingsView(auth_mixins.LoginRequiredMixin, views.View):
    template_name = "core/settings.html"

    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = {}
        context.update(kwargs)
        return context


# ================================================ #
# Authentication views                             #
# ================================================ #

# Login view
class LoginView(auth_views.LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True
    enable_recaptcha = True

    def form_valid(self, form):
        verified = True
        if self.enable_recaptcha:
            g_recaptcha_response = self.request.POST.get("g-recaptcha-response")
            url = settings.GOOGLE_RECAPTCHA_VERIFICATION_URL
            data = {
                "secret": settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                "response": g_recaptcha_response,
            }
            # Getting response from recaptcha server
            response = requests.post(url, data=data).json()
            if not response.get("success"):
                verified = False
        if verified:
            return super().form_valid(form)
        return super().form_invalid(form)


# Logout view
class LogoutView(auth_views.LogoutView):
    template_name = "registration/logged_out.html"


# Signup view
class SignupView(views.CreateView):
    template_name = "registration/logged_out.html"
    model = USER
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        return super().form_valid(form)


# ================================================ #
# Password Reset views                             #
# ================================================ #
class PasswordResetView(auth_views.PasswordResetView):
    email_template_name = "registration/password_reset_email.html"
    from_email = None
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("core:password_reset_done")
    template_name = "registration/password_reset_form.html"


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy("core:password_reset_complete")
    template_name = "registration/password_reset_confirm.html"


# ================================================ #
# Password Change views                            #
# ================================================ #
class PasswordChangeView(auth_mixins.LoginRequiredMixin, auth_views.PasswordChangeView):
    success_url = reverse_lazy("core:password_change_done")
    template_name = "registration/password_change_form.html"


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = "registration/password_change_done.html"


# ================================================ #
# Product Related views                            #
# ================================================ #
# category view
class CategoryListView(views.ListView):
    template_name = "core/category_list.html"
    model = CategoryModel
    paginate_by = 20
    context_object_name = "categories"


# Product by category
class ProductListByCategory(views.ListView):
    template_name = "core/shop.html"
    model = ProductModel
    paginate_by = 5
    context_object_name = "products"

    def get_queryset(self):
        qs = super().get_queryset()
        pk = int(self.kwargs.get("pk"))
        qs = qs.filter(category__id=pk)
        return qs


# Product Detail view
class ProductDetailView(views.DetailView):
    template_name = "core/product_detail.html"
    model = ProductModel
    context_object_name = "product"

    def get_queryset(self):
        qs = super().get_queryset()
        product = qs.first()
        print(product.get_review())

        return qs
    


# Product add Review view
class ProductReviewAddView(auth_mixins.LoginRequiredMixin, views.View):
    template_name = "core/product_review_add.html"
    form_class = ProductReviewForm
    success_url = reverse_lazy("core:shop")

    def get(self, request, **kwargs):
        product_id = kwargs.get("pk")
        product = ProductModel.objects.filter(id=product_id).first()

        context = {"form": self.form_class(), "product": product}

        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        try:
            user = self.request.user
            product_id = self.kwargs.get("pk")
            product = ProductModel.objects.get(id=product_id)
            form.instance.user = user
            form.instance.product = product
            form.save()
            messages.success(self.request, "Review added successfully!")
        except:
            messages.error(self.request, "Sorry! Could't add review!")
            return self.form_invalid(form)
        return redirect(self.success_url)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {"form": form})


# Wishlist Create view
class WishlistCreateView(auth_mixins.LoginRequiredMixin, views.CreateView):
    template_name = "core/wishlist_create.html"
    model = WishlistModel
    form_class = WishlistForm
    success_url = reverse_lazy("core:wishlist_list")

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        return super().form_valid(form)


# Wishlist listing view
class WishlistListView(auth_mixins.LoginRequiredMixin, views.ListView):
    template_name = "core/whishlist_list.html"
    context_object_name = "wishlists"
    model = WishlistModel

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        qs = qs.filter(status=True, user=user)
        return qs


# Wishlist detail view
class WishlistDetailView(auth_mixins.LoginRequiredMixin, views.DetailView):
    template_name = "core/whishlist_detail.html"
    context_object_name = "wishlist"
    model = WishlistModel
    extra_context = {
        "wishlist_action": "remove from",
        "wishlist_action_link": "remove_from_wishlist",
    }


class AddToWishlist(auth_mixins.LoginRequiredMixin, views.View):
    template_name = "core/whishlist_add.html"
    wishlist_model = WishlistModel
    product_model = ProductModel
    add_to_wishlist_form = AddToWishlistFormSet

    def get(self, request, **kwargs):
        user = request.user
        wishlists = self.wishlist_model.objects.filter(status=True, user=user)
        product_id = kwargs.get("product_pk", None)
        product = None
        try:
            product = self.product_model.objects.get(id=product_id)
        except:
            pass

        print(product.wishlistmodel_set.all())

        context = {
            "product": product,
            "form": self.add_to_wishlist_form(),
            "wishlists": wishlists,
            "wishlist_action": "add to",
        }

        return render(request, self.template_name, context)

    def post(self, request, **kwargs):

        product_id = kwargs.get("product_pk", None)
        wishlist_ids = request.POST.getlist("wishlists")
        try:
            product = self.product_model.objects.get(id=product_id)
            wishlists = [
                wishlist
                for wishlist in self.wishlist_model.objects.filter(id__in=wishlist_ids)
            ]
            product.wishlistmodel_set.set(wishlists)
            messages.success(request, f"{product} Updated successfully!")
        except Exception as e:
            messages.error(request, f"Something is went wrong! ERROR: {e}")

        url = self.request.META.get("HTTP_REFERER")
        return redirect(url)


# Remove product from wishlist
class RemoveFromWishlistView(auth_mixins.LoginRequiredMixin, views.View):
    def post(self, request, **kwargs):
        product_id = kwargs.get("product_id", None)
        wishlist_id = request.POST.get("wishlist_id", None)

        try:
            wishlist = WishlistModel.objects.get(id=wishlist_id)
            wishlist.products.remove(product_id)
            wishlist.save()
            messages.success(request, "Product removed from wishlist successfully!")
        except:
            messages.error(request, "Sorry, Can not remove product from wishlist!")

        url = self.request.META.get("HTTP_REFERER")
        return redirect(url)


# ================================================ #
# Cart Related views                               #
# ================================================ #
# add item to cart
class AddToCartView(auth_mixins.LoginRequiredMixin, views.View):
    def post(self, request):
        user = request.user
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity"))

        try:
            product = ProductModel.objects.filter(
                id=product_id,
                status=True,
            ).first()

            cart, cart_created = Cart.objects.get_or_create(
                user=user,
                status=True,
                checked_out=False,
            )

            if cart_created:
                cart.empty = False
                cart.save()

            cart_item, cart_item_created = CartItem.objects.get_or_create(
                cart=cart,
                status=True,
                product=product,
            )

            if cart_item_created:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity

            cart_item.save()
            messages.success(request, "Added successfully!")

        except:
            messages.error(request, "Something is went wrong!")

        url = request.META.get("HTTP_REFERER")
        return redirect(url)


# update/delete cart items
class CartView(auth_mixins.LoginRequiredMixin, views.View):
    template_name = "core/cart.html"
    form_class = CartItemFormSet
    model = CartItem
    currency_form = CurrencyForm

    def get(self, request):
        cart = Cart.get_cart(request)
        cart_items = cart.items()
        form = self.form_class(queryset=cart_items)
        context = {
            "form": form,
            "currency_form": self.currency_form(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        cart = Cart.get_cart(request)
        cart_items = cart.items()
        form = self.form_class(request.POST, initial=cart_items)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):

        currency_form = self.currency_form(self.request.POST)
        if currency_form.is_valid():
            currency = currency_form.cleaned_data.get("currency")

        self.request.session["currency"] = currency or None

        form.save()

        messages.success(self.request, "Cart updated successfully!")

        url = self.request.META.get("HTTP_REFERER")
        return redirect(url)

    def form_invalid(self, form):
        context = {"formset": form}
        messages.error(self.request, "Cart updation failed!")
        return render(self.request, self.template_name, context)


# ================================================ #
# Checkout Related views                           #
# ================================================ #
class CheckoutView(auth_mixins.LoginRequiredMixin, views.View):
    template_name = "core/checkout.html"
    billing_address_form = BillingAddressForm
    shipping_address_form = ShippingAddressForm

    def get(self, request):
        address = None
        if hasattr(request.user, "profile"):
            address = request.user.profile.address or None

        context = {
            "billing_form": self.billing_address_form(instance=address),
            "shipping_form": self.shipping_address_form(),
        }

        return render(request, self.template_name, context)

    def post(self, request):
        same_as_billing_address = request.POST.get("same_as_billing_address", None)
        billing_form = shipping_form = self.billing_address_form(request.POST)

        if not same_as_billing_address:
            shipping_form = self.shipping_address_form(request.POST)

        if billing_form.is_valid() and shipping_form.is_valid():
            return self.form_valid(billing_form, shipping_form)

        return self.form_invalid(billing_form, shipping_form)

    def apply_other_charges(self, amount):
        cost = amount + 0
        return cost

    def get_delivery_charge(self, shipping_address):
        cost = 0
        return cost

    def form_valid(self, billing_form, shipping_form):
        currency = self.request.session.get("currency")
        cart = Cart.get_cart(self.request)
        billing_address = billing_form.save()
        shipping_address = shipping_form.save()
        delivery_charge = self.get_delivery_charge(shipping_address)
        amount = self.apply_other_charges(cart.total() + delivery_charge)

        # create order
        data = {
            "amount": amount,
            "currency": currency,
            "payment_capture": 0,
        }
        razorpay_order = RAZORPAY_CLIENT.order.create(data=data)
        id = razorpay_order.get("id", None)

        Order.objects.create(
            id=id,
            cart=cart,
            amount=amount,
            delivery_charge=delivery_charge,
            billing_address=billing_address,
            shipping_address=shipping_address,
        )

        return redirect(reverse_lazy("core:payment_handler"))

    def form_invalid(self, billing_form, shipping_form):
        context = {
            "billing_form": billing_form,
            "shipping_form": shipping_form,
        }
        return render(self.request, self.template_name, context)


class OrderView(auth_mixins.LoginRequiredMixin, views.ListView):
    template_name = "core/order.html"
    model = Order
    context_object_name = "orders"

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        qs = qs.filter(cart__user=user)
        return qs


# Order detail
class OrderDetailView(auth_mixins.LoginRequiredMixin, views.DetailView):
    template_name = "core/order_detail.html"
    model = Order
    context_object_name = "order"

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        qs = qs.filter(cart__user=user)
        return qs


# Order history
class OrderHistoryView(auth_mixins.LoginRequiredMixin, views.View):
    template_name = "core/order_history.html"
    model = Order

    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        user = self.request.user
        orders = Order.objects.filter(cart__user=user)
        context = {"orders": orders}
        context.update(kwargs)
        return context


# ================================================ #
# Payment Realated views                           #
# ================================================ #
# Payment view
class PaymentView(auth_mixins.LoginRequiredMixin, views.View):
    template_name = "core/pay.html"

    def get(self, request):
        cart = Cart.get_cart(self.request)
        order = Order.objects.filter(
            cart=cart,
            completed=False,
        ).last()
        context = {
            "razorpay_order_id": order.id,
            "razorpay_merchant_key": settings.RAZORPAY_KEY_ID,
            "razorpay_amount": order.amount,
            "razorpay_currency": order.currency,
            "razorpay_callback_url": reverse_lazy("core:payment_handler"),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        try:
            # get the required parameters from post request.
            payment_id = request.POST.get("razorpay_payment_id", "")
            razorpay_order_id = request.POST.get("razorpay_order_id", "")
            signature = request.POST.get("razorpay_signature", "")
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }

            order = Order.objects.filter(id=razorpay_order_id).last()

            # verify the payment signature.
            result = RAZORPAY_CLIENT.utility.verify_payment_signature(params_dict)
            if result is not None:
                amount = order.amount
                try:

                    # capture the payemt
                    RAZORPAY_CLIENT.payment.capture(payment_id, amount)

                    Payment.objects.create(
                        id=payment_id,
                        order=order,
                        status=Payment.PaymentStatusChoices.completed,
                        mode="",
                    )

                    # render success page on successful caputre of payment
                    return render(request, "core/paymentsuccess.html")
                except:

                    # if there is an error while capturing payment.
                    return render(request, "core/paymentfail.html")
            else:

                # if signature verification fails.
                return render(request, "core/paymentfail.html")
        except:

            # if we don't find the required parameters in POST data
            return redirect(reverse_lazy("core:payment_handler"))


# Payment List view
class PaymentListView(auth_mixins.LoginRequiredMixin, views.ListView):
    template_name = "core/payment_list.html"
    model = Payment
    context_object_name = "payments"

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        qs = qs.filter(order__cart__user=user)
        return qs
