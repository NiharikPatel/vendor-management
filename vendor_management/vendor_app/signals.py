from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PurchaseOrder, HistoricalPerformance
from django.utils import timezone
from django.db import models
from django.db.models import Avg


@receiver(post_save, sender=PurchaseOrder)
def update_vendor_performance(sender, instance, created, **kwargs):
    
    if  instance.status == 'completed':
        print("signal working")
        def calculate_on_time_delivery_rate(vendor):
            completed_purchases = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
            on_time_deliveries = completed_purchases.filter(acknowledgment_date__lte=models.F('delivery_date'))
            total_completed_purchases = completed_purchases.count()
            if total_completed_purchases == 0:
                return 0.0
            round_on_time_deliver_rate = round((on_time_deliveries.count() / total_completed_purchases),2)
            return round_on_time_deliver_rate
        
        def calculate_quality_rating_avg(vendor):
            completed_purchases = PurchaseOrder.objects.filter(vendor=vendor, status='completed',
                                                               quality_rating__isnull=False)
            total_ratings = completed_purchases.count()
            if total_ratings == 0:
                return 0.0
            quality_ratings_sum = completed_purchases.aggregate(models.Sum('quality_rating'))['quality_rating__sum']
            round_quality_rating =round((quality_ratings_sum / total_ratings),2) 
            return round_quality_rating
    
        def calculate_average_response_time(vendor):
            acknowledged_purchases = PurchaseOrder.objects.filter(vendor=vendor, acknowledgment_date__isnull=False)
            total_acknowledged_purchases = acknowledged_purchases.count ()
            if total_acknowledged_purchases == 0:
                return 0.0
            response_time_sum = sum((purchase.acknowledgment_date - purchase.issue_date).days for purchase in
                                    acknowledged_purchases)
            round_response_time = round((response_time_sum / total_acknowledged_purchases),0)
            return round_response_time
        
        def calculate_fulfillment_rate(vendor):
            issued_purchases = PurchaseOrder.objects.filter(vendor=vendor)
            completed_purchases = issued_purchases.filter(status='completed', issue_date__isnull=True)
            total_issued_purchases = issued_purchases.count()
            if total_issued_purchases == 0:
                return 0.0
            round_fulfillment_rate = round((completed_purchases.count() / total_issued_purchases),2)
            return round_fulfillment_rate
    
            # Assuming you have a method to calculate performance metrics
        on_time_delivery_rate = calculate_on_time_delivery_rate(instance.vendor)
        quality_rating_avg = calculate_quality_rating_avg(instance.vendor)
        average_response_time = calculate_average_response_time(instance.vendor)
        fulfillment_rate = calculate_fulfillment_rate(instance.vendor)
        # Update or create a HistoricalPerformance record
        HistoricalPerformance.objects.update_or_create(
            vendor=instance.vendor,
            date=timezone.now(),
            on_time_delivery_rate=on_time_delivery_rate,
            quality_rating_avg=quality_rating_avg,
            average_response_time=average_response_time,
            fulfillment_rate=fulfillment_rate
        )
# signal for updating vendor model with percentage and average of Historical Performance metrics
        
@receiver(post_save, sender=HistoricalPerformance)    
def update_performance(sender, instance, created, **kwargs):
    if created:
        vendor = instance.vendor

        average_on_time_delivery_rate = HistoricalPerformance.objects.filter(vendor = vendor).aggregate( avg_on_time_delivery_rate = Avg('on_time_delivery_rate')
        )['avg_on_time_delivery_rate'] or 0.0
        average_on_time_delivery_rate *= 100

        average_quality_rating_avg = HistoricalPerformance.objects.filter(vendor=vendor).aggregate(
            avg_quality_rating_avg=Avg('quality_rating_avg')
        )['avg_quality_rating_avg'] or 0.0

        average_response_time = HistoricalPerformance.objects.filter(vendor=vendor).aggregate(
            avg_response_time=Avg('average_response_time')
        )['avg_response_time'] or 0.0

        average_fulfillment_rate = HistoricalPerformance.objects.filter(vendor=vendor).aggregate(
            avg_fulfillment_rate=Avg('fulfillment_rate')
        )['avg_fulfillment_rate'] or 0
        average_fulfillment_rate *= 100

        vendor.on_time_delivery = average_on_time_delivery_rate
        vendor.quality_rating_avg = average_quality_rating_avg
        vendor.average_response_time = average_response_time
        vendor.fulfillment_rate = average_fulfillment_rate

        vendor.save()