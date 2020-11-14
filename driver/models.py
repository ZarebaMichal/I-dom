from django.db import models


class Drivers(models.Model):

    CATEGORIES = [
        ('remote_control', 'remote_control'),
        ('roller_blind', 'roller_blind'),
        ('clicker', 'clicker'),
        ('bulb', 'bulb'),
    ]
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(max_length=30, unique=True)
    category = models.CharField(max_length=15, choices=CATEGORIES)
    is_active = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    data = models.BooleanField(null=True)

    class Meta:
        verbose_name = "Driver"
        verbose_name_plural = "Drivers"

    def __str__(self):
        return str(self.id)
