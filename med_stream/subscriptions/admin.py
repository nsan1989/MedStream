from import_export import resources
from import_export.admin import ImportExportModelAdmin


from django.contrib import admin
from .models import SubscriptionPlan


# Subscription plan resources.
class SubscriptionPlanResource(resources.ModelResource):
    class Meta:
        model = SubscriptionPlan
        fields = (
            "id",
            "name",
            "slug",
            "billing_cycle",
            "price",
            "duration_days",
            "trial_days",
            "max_users",
            "max_facilities",
            "max_storage",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )


# Subscription plan admin.
@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(ImportExportModelAdmin):
    resource_class = SubscriptionPlanResource
    list_display = (
        "name",
        "billing_cycle",
        "price",
        "duration_days",
        "trial_days",
        "max_users",
        "max_facilities",
        "max_storage",
        "is_active",
    )
    list_filter = ("billing_cycle", "is_active")
    search_fields = ("name", "slug")
