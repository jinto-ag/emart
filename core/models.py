from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.db.models import Sum, F, Q, Avg


class User(AbstractUser):
    pass


# ======================================================== #
# Global Variables                                         #
# ======================================================== #

USER = get_user_model()

# ======================================================== #
# Abstract Models                                          #
# ======================================================== #
class TimeStamp(models.Model):
    status = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Location(TimeStamp, models.Model):
    longitude = models.FloatField()
    lattitude = models.FloatField()

    def __str__(self):
        return f"{self.longitude},{self.lattitude}"


class Address(TimeStamp, models.Model):
    building_name = models.CharField(max_length=120)
    place = models.CharField(max_length=64)
    street = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    district = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    country = models.CharField(max_length=64)
    post_office = models.CharField(max_length=64)
    post_code = models.CharField(max_length=64)
    location = models.ForeignKey(
        "Location", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.building_name}\n{self.place}\n{self.district}\n{self.state} - {self.post_code}"

    @staticmethod
    def get_obj_for_profile(request, **kwargs):
        user = request.user
        obj = Address.objects.filter(profile__user=user, status=True, **kwargs).first()
        return obj


class Feedback(TimeStamp, models.Model):
    name = models.CharField(max_length=60)
    email = models.EmailField(max_length=60)
    subject = models.CharField(max_length=120, default="I want to know more.")
    message = models.TextField(max_length=500)
    is_replied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"


class FeedbackReply(TimeStamp, models.Model):
    feedback = models.OneToOneField(Feedback, on_delete=models.CASCADE)
    reply = models.TextField(max_length=500)
    user = models.ForeignKey(USER, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.feedback.subject}"


# ======================================================== #
# User Related Models                                      #
# ======================================================== #
class Profile(TimeStamp, models.Model):
    class GenderChoices:
        male = "m"
        female = "f"
        transgender = "t"

    class AccountTypeChoices:
        customer = "customer"
        administrator = "admin"

    GENDER_CHOICES = (
        (GenderChoices.male, "Male"),
        (GenderChoices.female, "Female"),
        (GenderChoices.transgender, "Transgender"),
    )

    ACCOUNT_TYPE_CHOICES = (
        ("Customer", AccountTypeChoices.customer),
        ("Administrator", AccountTypeChoices.administrator),
    )

    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    gender = models.CharField(max_length=12, choices=GENDER_CHOICES)
    address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True
    )
    image = models.ImageField(
        upload_to="user/profile/image", default="default/user.png"
    )
    account_type = models.CharField(
        max_length=16,
        choices=ACCOUNT_TYPE_CHOICES,
        default=AccountTypeChoices.customer,
    )
    user = models.OneToOneField(USER, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_loyal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @staticmethod
    def get_obj(request, **kwargs):
        user = request.user
        obj = Profile.objects.filter(user=user, status=True, **kwargs).first()
        return obj


# ======================================================== #
# Product Related Models                                   #
# ======================================================== #
class CategoryModel(TimeStamp, models.Model):
    name = models.CharField(max_length=48)
    image = models.ImageField(
        upload_to="category/image/", default="default/category.png"
    )
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(USER, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("product:category_detail", kwargs={"pk": self.pk})


class UnitModel(TimeStamp, models.Model):
    name = models.CharField(max_length=16)
    symbol = models.CharField(max_length=16)
    convertion_rate = models.FloatField()
    secondary = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(USER, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("product:unit_detail", kwargs={"pk": self.pk})


class ProductModel(TimeStamp, models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(max_length=500)
    price = models.FloatField()
    image = models.ImageField(upload_to="product/image/", default="default/product.png")
    category = models.ForeignKey(
        CategoryModel, on_delete=models.SET_NULL, null=True, blank=True
    )
    unit = models.ForeignKey(
        UnitModel, on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(USER, on_delete=models.CASCADE)

    # products = ProductManager()

    def __str__(self) -> str:
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("product:product_detail", kwargs={"pk": self.pk})

    def get_review(self):
        reviews = (
            self.reviewmodel_set.annotate(
                product_review=F("rating")
            )
            .aggregate(Avg("product_review"))
            .get("product_review__avg")
        )

        return reviews


class ReviewModel(TimeStamp, models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    rating = models.FloatField()
    comment = models.TextField(max_length=250)
    user = models.ForeignKey(USER, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user} ({self.rating})"

    def get_absolute_url(self):
        return reverse("product:review_detail", kwargs={"pk": self.pk})


class WishlistModel(TimeStamp, models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(max_length=500, blank=True, default="")
    products = models.ManyToManyField(ProductModel, blank=True)
    user = models.ForeignKey(USER, on_delete=models.CASCADE, blank=True)

    def __str__(self) -> str:
        return self.name


# ======================================================== #
# Cart Related Models                                      #
# ======================================================== #
class Cart(TimeStamp, models.Model):
    user = models.ForeignKey(USER, on_delete=models.CASCADE)
    empty = models.BooleanField(default=True)
    checked_out = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}"

    def total(self):
        price = (
            (
                CartItem.objects.filter(cart=self, status=True).annotate(
                    item_price=F("quantity") * F("product__price")
                )
            )
            .aggregate(Sum("item_price"))
            .get("item_price__sum")
        )

        return price

    def items(self):
        cart_items = CartItem.objects.filter(cart__user=self.user, status=True)
        return cart_items

    @staticmethod
    def get_cart(request, **kwargs):
        user = request.user
        cart, created = Cart.objects.get_or_create(
            user=user,
            status=True,
            checked_out=False,
            **kwargs,
        )
        return cart


class CartItem(TimeStamp, models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product} ({self.quantity})"

    def total(self):
        cost = self.product.price * self.quantity
        return cost

    def __iter__(self):
        return self.__next__()

    def __next__(self):
        yield (self.product, self.quantity)


class Order(TimeStamp, models.Model):
    class CurrencyChoices:
        INR = "INR"
        DOLLAR = "D"

    CURRENCY_CHOICES = (
        ("Indian Rupee", CurrencyChoices.INR),
        ("Dollar", CurrencyChoices.DOLLAR),
    )

    id = models.CharField(primary_key=True, unique=True, max_length=120)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    amount = models.FloatField()
    currency = models.CharField(
        max_length=24,
        choices=CURRENCY_CHOICES,
        default=CurrencyChoices.INR,
    )
    delivery_charge = models.FloatField(default=0)
    completed = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checkout_billing_address",
    )
    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checkout_shipping_address",
    )

    def __str__(self) -> str:
        return f"{self.id or self.cart} {'Completed' if self.completed else 'Not Completed'}"

    def total(self):
        cart_total = self.cart.total
        cost = cart_total + self.delivery_charge
        return cost


class Payment(TimeStamp, models.Model):
    class PaymentStatusChoices:
        pending = "pending"
        completed = "completed"
        failed = "failed"

    PAYMENT_STATUS_CHOICES = (
        ("Pending", PaymentStatusChoices.pending),
        ("Completed", PaymentStatusChoices.completed),
        ("Failed", PaymentStatusChoices.failed),
    )

    id = models.CharField(primary_key=True, unique=True, max_length=120)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=16,
        choices=PAYMENT_STATUS_CHOICES,
        default=PaymentStatusChoices.pending,
    )
    mode = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.status}"
