from rest_framework import permissions


class IsTutor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'tutor'


class IsTutorCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.role == 'tutor':
            if hasattr(obj, 'tutor'):
                return obj.tutor.user == request.user
            return obj.education_plan.tutor.user == request.user
        return False
