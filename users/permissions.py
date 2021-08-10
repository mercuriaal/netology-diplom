from rest_framework.permissions import BasePermission


class Partner(BasePermission):

    message = 'Только для поставщиков'

    def has_permission(self, request, view):
        return request.user.type == 'partner'


class Client(BasePermission):

    message = 'Только для клиентов'

    def has_permission(self, request, view):
        return request.user.type == 'client'


class Owner(BasePermission):

    message = 'Только для владельцев'

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
