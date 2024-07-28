try:

    from django.contrib import admin
    from .models import Product, Variant

    class VariantInlineAdmin(admin.TabularInline):
        model = Variant
        min_num = 1
        extra = 0

    class ProductAdmin(admin.ModelAdmin):
        list_display = ["__str__", "nonveg", "restaurant"]
        list_filter = ["restaurant", "category", "nonveg"]
        inlines = [VariantInlineAdmin]

    # Register your models here.
    admin.site.register(Product, ProductAdmin)

except:
    pass
