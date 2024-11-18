from rest_framework.permissions import BasePermission

class isStudentPermission(BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Student'

class isTeacherPermission(BasePermission):
    
    def has_permission(self, request, view):
        return  request.user.is_authenticated and request.user.role == 'Teacher'

class isAdminPermission(BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Admin'
