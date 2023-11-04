from rest_framework import permissions


class IsTutor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'tutor'


class IsTutorCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.role == 'tutor' and obj.tutor.user == request.user
