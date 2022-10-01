from django.contrib import admin

from core import models


# user realted models
admin.site.register(models.User)
admin.site.register(models.Profile)
admin.site.register(models.Location)
admin.site.register(models.Address)
admin.site.register(models.Feedback)
admin.site.register(models.FeedbackReply)
admin.site.register(models.ReviewModel)

# Product related models
admin.site.register(models.UnitModel)
admin.site.register(models.CategoryModel)
admin.site.register(models.ProductModel)
admin.site.register(models.WishlistModel)

# cart related models
admin.site.register(models.Cart)
admin.site.register(models.CartItem)
admin.site.register(models.Order)
admin.site.register(models.Payment)
