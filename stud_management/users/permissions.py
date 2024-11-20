from rest_framework.permissions import BasePermission

class isStudentPermission(BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class isTeacherPermission(BasePermission):
    
    def has_permission(self, request, view):
        return  request.user.is_authenticated and request.user.role == 'teacher'

class isAdminPermission(BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'
