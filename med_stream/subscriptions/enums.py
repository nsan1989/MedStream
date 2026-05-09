from django.db import models


# Subscription status choices.
class SubscriptionChoices(models.TextChoices):
    MONTHLY = (
        "MONTHLY",
        "Monthly",
    )
    QUATERLY = (
        "QUARTERLY",
        "Quarterly",
    )
    YEARLY = (
        "YEARLY",
        "Yearly",
    )
    FREE_TRIAL = (
        "FREE_TRIAL",
        "Free Trial",
    )
