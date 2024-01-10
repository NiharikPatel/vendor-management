from django.db import models
from .models import PurchaseOrder
from datetime import timezone


def calculate_on_time_delivery_rate(vendor):
    date = timezone.now()
    completed_purchases = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
    on_time_deliveries = completed_purchases.filter(date <= models.F('delivery_date'))

    total_completed_purchases = completed_purchases.count()

    if total_completed_purchases == 0:
        return 0.0

    return on_time_deliveries.count() / total_completed_purchases


def calculate_quality_rating_avg(vendor):
    completed_purchases = PurchaseOrder.objects.filter(vendor=vendor, status='completed', quality_rating__isnull=False)

    total_ratings = completed_purchases.sum()

    if total_ratings == 0:
        return 0.0

    quality_ratings_sum = completed_purchases.aggregate(models.Sum('quality_rating'))['quality_rating__sum']

    return quality_ratings_sum / total_ratings


def calculate_average_response_time(vendor):
    acknowledged_purchases = PurchaseOrder.objects.filter(vendor=vendor,  acknowledgment_date__isnull=False)

    total_acknowledged_purchases = acknowledged_purchases.count()

    if total_acknowledged_purchases == 0:
        return 0.0

    response_time_sum = sum((purchase.acknowledgment_date - purchase.issue_date).total_seconds() for purchase in acknowledged_purchases)

    return response_time_sum / total_acknowledged_purchases


def calculate_fulfillment_rate(vendor):
    issued_purchases = PurchaseOrder.objects.filter(vendor=vendor)
    completed_purchases = issued_purchases.filter(status='completed', issues__isnull=True)

    total_issued_purchases = issued_purchases.count()

    if total_issued_purchases == 0:
        return 0.0

    return completed_purchases.count() / total_issued_purchases
