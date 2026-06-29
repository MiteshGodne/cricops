from django.db import models
import uuid

class Venue(models.Model):
    venue_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    pincode = models.IntegerField(null=True)
    capacity = models.BigIntegerField(blank=True, null=True)
    gps_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    gps_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL,null=True, blank=True,related_name='created_venues')
    class Meta:
        db_table = 'venues'
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.city}"