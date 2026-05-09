from import_export import resources
from import_export.admin import ImportExportModelAdmin


from django.contrib import admin
from .models import Organization, OrganizationBranding, OrganizationSubscription


# Organization resources.
class OrganizationResource(resources.ModelResource):
    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "slug",
            "organization_type",
            "registration_number",
            "email",
            "phone_number",
            "website",
            "description",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "postal_code",
            "is_active",
            "is_verified",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )


# Organization admin.
@admin.register(Organization)
class OrganizationAdmin(ImportExportModelAdmin):
    resource_class = OrganizationResource
    list_display = ("name", "organization_type", "email", "phone_number", "is_active")
    search_fields = ("name", "email", "phone_number")
    list_filter = ("organization_type", "is_active", "is_verified")


# Organization branding resources.
class OrganizationBrandingResource(resources.ModelResource):
    class Meta:
        model = OrganizationBranding
        fields = (
            "organization",
            "logo",
            "favicon",
            "primary_color",
            "secondary_color",
            "login_banner",
        )


# Organization branding admin.
@admin.register(OrganizationBranding)
class OrganizationBrandingAdmin(ImportExportModelAdmin):
    resource_class = OrganizationBrandingResource
    list_display = ("organization", "primary_color", "secondary_color")
    search_fields = ("organization__name",)


# Organization subscription resources.
class OrganizationSubscriptionResource(resources.ModelResource):
    class Meta:
        model = OrganizationSubscription
        fields = (
            "id",
            "organization",
            "subscription_plan",
            "start_date",
            "end_date",
            "status",
            "auto_renew",
            "is_trial",
            "amount_paid",
            "created_at",
            "updated_at",
        )


# Organization subscription admin.
@admin.register(OrganizationSubscription)
class OrganizationSubscriptionAdmin(ImportExportModelAdmin):
    resource_class = OrganizationSubscriptionResource
    list_display = (
        "organization",
        "subscription_plan",
        "start_date",
        "end_date",
        "status",
        "auto_renew",
        "is_trial",
        "amount_paid",
    )
    search_fields = ("organization__name", "subscription_plan__name")
    list_filter = ("status", "auto_renew", "is_trial")
