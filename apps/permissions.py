from rest_framework.permissions import BasePermission
'''En estaas lineas de codigo usamos permisos 
para dar acceso a los administradores y solo permitir el ingreso 
a usuarios autentificados como los votantes, y estos permisos tambien van 
enlazados a las vistas en elecciones view.

Solo permite acceso a usuarios administradores
Solo permite acceso a usuarios autenticados no admin

'''
class EsAdmin(BasePermission):
  
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class EsVotante(BasePermission):
   
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated