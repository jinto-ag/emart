from django.urls import path
from core import views

app_name = "core"


urlpatterns = [
    # Common
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("news/", views.NewsView.as_view(), name="news"),
    path("shop/", views.ShopView.as_view(), name="shop"),
    # User
    path("user/profile/", views.ProfileView.as_view(), name="profile"),
    path("user/dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("user/settings/", views.SettingsView.as_view(), name="settings"),
    # Authentication urls
    path("user/login/", views.LoginView.as_view(), name="login"),
    path("user/signup/", views.SignupView.as_view(), name="signup"),
    path("user/logout/", views.LogoutView.as_view(), name="logout"),
    # Password Reset
    path("user/password_reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path("user/password_reset/done/", views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("user/reset/<uidb64>/<token>/", views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("user/reset/done/", views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    # Password Change
    path("user/password_change/", views.PasswordChangeView.as_view(), name="password_change"),
    path("user/password_change/done/", views.PasswordChangeDoneView.as_view(), name="password_change_done"),
    # Product
    path("product/<int:pk>/detail/", views.ProductDetailView.as_view(), name="product_detail"),
    path("product/category/", views.CategoryListView.as_view(), name="category_list"),
    path("product/category/<int:pk>/product/", views.ProductListByCategory.as_view(), name="product_by_category"),
    # Product Review
    path("product/<int:pk>/review/", views.ProductReviewAddView.as_view(), name="add_product_review"),
    # Wishlist
    path("wishlist/", views.WishlistListView.as_view(), name="wishlist_list"),
    path("wishlist/create/", views.WishlistCreateView.as_view(), name="wishlist_create"),
    path("wishlist/<int:pk>/", views.WishlistDetailView.as_view(), name="wishlist_detail"),
    path("wishlist/add/product/<int:product_pk>/", views.AddToWishlist.as_view(), name="add_to_wishlist"),
    path("wishlist/remove/product/<int:product_pk>/", views.AddToWishlist.as_view(), name="remove_from_wishlist"),
    # Cart
    path("cart/", views.CartView.as_view(), name="cart"),
    path("cart/add/", views.AddToCartView.as_view(), name="cart_add"),
    path("cart/checkout/", views.CheckoutView.as_view(), name="cart_checkout"),
    path("cart/payment/", views.PaymentView.as_view(), name="cart_payment"),
    # Payment
    path("payment/", views.PaymentListView.as_view(), name="payment_list"),
    # Order
    path("order/history/", views.OrderHistoryView.as_view(), name="order_history"),
    path("order/", views.OrderView.as_view(), name="order"),
    path("order/<str:pk>/", views.OrderDetailView.as_view(), name="order_detail"),

]
