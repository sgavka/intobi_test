import datetime
import json

from django.db.models import Avg, F
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ListSerializer
from rest_framework.views import APIView
from rest_framework import viewsets, mixins, status
from rest_framework.viewsets import GenericViewSet

from app.models import Restaurant, Menu, Employee, Vote
from app.serializers import RestaurantSerializer, MenuSerializer, EmployeeSerializer, VoteSerializer


class MenuView(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = (IsAuthenticated,)


class CurrentDayMenuView(mixins.CreateModelMixin, GenericViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        try:
            query_set = Menu.objects.filter(date=datetime.datetime.now().date(),
                                            restaurant_id=self.request.user.employee.get().restaurant_id)\
                .order_by('id')
            if request.version == 'v1.0':
                instance = query_set.first()
            else:
                instance = query_set.all()
        except Menu.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Employee.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if request.version == 'v1.0':
            serializer = self.get_serializer(instance)
        else:
            serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)

    def vote(self, request, *args, **kwargs):
        now_from = datetime.datetime.now()
        now_from.replace(hour=0, minute=0, second=0, microsecond=0)
        now_to = datetime.datetime.now()
        now_to.replace(hour=12, minute=0, second=0, microsecond=0)

        if not (now_from < datetime.datetime.now() < now_to):
            raise ValidationError('You can vote only before lunch.')

        employee = self.request.user.employee.get()
        menu_query_set = Menu.objects.filter(date=datetime.datetime.now().date(),
                                             restaurant_id=employee.restaurant_id)
        data = request.data
        if request.version == 'v1.0':
            menu = menu_query_set.first()
            if not menu:
                return Response(status=status.HTTP_404_NOT_FOUND)

            data['menu'] = menu.id
            data['employee'] = employee.id

            serializer_params = {'data': data}
        else:
            menu = menu_query_set.all()
            if not menu:
                return Response(status=status.HTTP_404_NOT_FOUND)

            for item in data:
                local_menu = next(i for i in menu if i.id == item['id'])
                if local_menu:
                    item['menu'] = item['id']
                    item['employee'] = employee.id

            serializer_params = {'data': data, 'many': True}

        serializer = VoteSerializer(**serializer_params)
        serializer.is_valid(raise_exception=True)

        if type(serializer) is ListSerializer:
            votes = serializer.validated_data
        else:
            votes = [serializer.validated_data]

        for vote in votes:
            Vote.objects.update_or_create(menu_id=vote['menu_id'], employee_id=vote['employee_id'],
                                          defaults={'value': vote['value']})

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def result(self, request, *args, **kwargs):
        try:
            employee = self.request.user.employee.get()
            query_set = Menu.objects.filter(date=datetime.datetime.now().date(), restaurant_id=employee.restaurant_id)
            if request.version == 'v1.0':
                menu = query_set.first()
                votes = Vote.objects.filter(menu=menu)
            else:
                menu = query_set.all()
                votes = Vote.objects.filter(menu__in=menu)

            votes = votes.values('menu_id').annotate(value=Avg('value'))
            votes = [{'id': item['menu_id'], 'value': item['value']} for item in votes]

            if request.version == 'v1.0':
                votes = next(iter(votes))

            return Response(votes)
        except Menu.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class RestaurantView(mixins.CreateModelMixin, GenericViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = (IsAuthenticated,)


class EmployeeView(mixins.CreateModelMixin, GenericViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = (IsAuthenticated,)


class HelloView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)
