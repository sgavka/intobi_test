import datetime
import json

from django.db.models import Avg
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, mixins, status
from rest_framework.viewsets import GenericViewSet

from app.models import Restaurant, Menu, Employee, Vote
from app.serializers import RestaurantSerializer, MenuSerializer, EmployeeSerializer, VoteSerializer


class MenuView(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    # permission_classes = [IsAccountAdminOrReadOnly]

    def get_queryset(self):
        if self.action == 'retrieve':
            return Menu.objects.filter(restaurant_id=self.kwargs['pk'])
        return super().get_queryset()


class CurrentDayMenuView(mixins.CreateModelMixin, GenericViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = Menu.objects.filter(
                date=datetime.datetime.now().date(),
                restaurant_id=self.request.user.employee.get().restaurant_id
            ).get()
        except Menu.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def vote(self, request, *args, **kwargs):
        try:
            employee = self.request.user.employee.get()
            menu = Menu.objects.filter(
                date=datetime.datetime.now().date(),
                restaurant_id=employee.restaurant_id
            ).get()

            data = request.data
            data['menu'] = menu.id
            data['employee'] = employee.id
            serializer = VoteSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Menu.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def result(self, request, *args, **kwargs):
        try:
            employee = self.request.user.employee.get()
            menu = Menu.objects.filter(
                date=datetime.datetime.now().date(),
                restaurant_id=employee.restaurant_id
            ).get()

            votes = Vote.objects.filter(menu=menu).aggregate(Avg('value'))

            return Response({
                'result': votes['value__avg']
            })
        except Menu.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class RestaurantView(mixins.CreateModelMixin, GenericViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    # permission_classes = [IsAccountAdminOrReadOnly]


class EmployeeView(mixins.CreateModelMixin, GenericViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class HelloView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)
