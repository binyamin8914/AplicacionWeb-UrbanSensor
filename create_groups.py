import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UrbanSensor.settings') 
django.setup()

from django.contrib.auth.models import Group, Permission

def create_groups_and_assign_permissions():
    
    grupos = ['SECPLA', 'Territorial', 'Direccion', 'Departamento', 'Cuadrilla']

    
    for nombre in grupos:
        group, created = Group.objects.get_or_create(name=nombre)
        if created:
            print(f"Grupo '{nombre}' creado.")
        else:
            print(f"Grupo '{nombre}' ya existe.")

    
    secpla_group = Group.objects.get(name='SECPLA')

    try:
        
        block_perm = Permission.objects.get(codename='can_block_user')
        
        secpla_group.permissions.add(block_perm)
        secpla_group.save()
        print("Permiso 'can_block_user' asignado al grupo SECPLA.")
    except Permission.DoesNotExist:
        print("ERROR: Permiso 'can_block_user' no encontrado. Verifica que esté creado y migrado.")

if __name__ == "__main__":
    create_groups_and_assign_permissions()
