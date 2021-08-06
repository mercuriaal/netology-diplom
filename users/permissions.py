from rest_framework.permissions import BasePermission


class Partner(BasePermission):

    def has_permission(self, request, view):
        return request.user.type == 'partner'


class Client(BasePermission):

    def has_permission(self, request, view):
        return request.user.type == 'client'


class Owner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
