from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Restaurant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name=_('Name'))
    owner = models.ForeignKey(User, models.CASCADE)


class Employee(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='employee')
    restaurant = models.ForeignKey(Restaurant, models.CASCADE)


class Menu(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    restaurant = models.ForeignKey(Restaurant, models.CASCADE)

    class Meta:
        unique_together = [('date', 'restaurant')]


class MenuItem(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name=_('Name'))
    menu = models.ForeignKey(Menu, models.CASCADE, related_name='items')


class Vote(models.Model):
    menu = models.ForeignKey(Menu, models.CASCADE)
    employee = models.ForeignKey(Employee, models.CASCADE)
    value = models.SmallIntegerField()

    class Meta:
        unique_together = [('menu', 'employee')]
