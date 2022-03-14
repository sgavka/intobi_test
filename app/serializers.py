from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.request import Request

from app.models import Restaurant, Menu, MenuItem, Employee, Vote


class RestaurantSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=empty, **kwargs):
        context = kwargs.get('context')
        if context:
            request = context.get('request')
            if request and hasattr(request, "user"):
                user = request.user
                data['owner'] = user.id
        super().__init__(instance, data, **kwargs)

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'owner')


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ('name',)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Employee
        fields = ('user',)

    def create(self, validated_data):
        with transaction.atomic():
            request: Request = self.context['request']
            pk = request.parser_context['kwargs']['pk']
            try:
                restaurant = Restaurant.objects.get(pk=pk)
            except Restaurant.DoesNotExist:
                raise serializers.ValidationError('Restaurant does not exists.')

            user = User.objects.create_user(validated_data['user']['username'],
                                            password=validated_data['user']['password'])
            employee = Employee.objects.create(user=user, restaurant=restaurant)

            return employee


class VoteSerializer(serializers.ModelSerializer):
    menu = serializers.IntegerField(write_only=True)
    employee = serializers.IntegerField(write_only=True)

    class Meta:
        model = Vote
        fields = ('value', 'menu', 'employee')


class MenuSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True)

    class Meta:
        model = Menu
        fields = ('date', 'items')

    def create(self, validated_data):
        with transaction.atomic():
            request: Request = self.context['request']
            pk = request.parser_context['kwargs']['pk']
            try:
                restaurant = Restaurant.objects.get(pk=pk)
            except Restaurant.DoesNotExist:
                raise serializers.ValidationError('Restaurant does not exists.')
            try:
                Menu.objects.get(date=validated_data['date'], restaurant=restaurant)
                raise serializers.ValidationError('Menu for this date already exists.')
            except Menu.DoesNotExist:
                menu = Menu.objects.create(date=validated_data['date'], restaurant=restaurant)

                for item_data in validated_data['items']:
                    item = MenuItem.objects.create(menu=menu, name=item_data['name'])

                return menu

    def validate_items(self, data):
        if len(data) == 0:
            raise serializers.ValidationError('Items can\'t be empty.')
        return data
