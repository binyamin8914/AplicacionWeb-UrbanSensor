import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UrbanSensor.settings') # Cambia por el nombre al de tu proyecto x.settings
django.setup()

from django.contrib.auth.models import Group, Permission

def create_groups_and_assign_permissions():
    # Lista de grupos a crear
    grupos = ['SECPLA', 'Territorial', 'Direccion', 'Departamento', 'Cuadrilla']

    # Crear grupos si no existen
    for nombre in grupos:
        group, created = Group.objects.get_or_create(name=nombre)
        if created:
            print(f"Grupo '{nombre}' creado.")
        else:
            print(f"Grupo '{nombre}' ya existe.")

    # Obtener el grupo SECPLA
    secpla_group = Group.objects.get(name='SECPLA')

    try:
        # Obtener permiso personalizado can_block_user
        block_perm = Permission.objects.get(codename='can_block_user')
        # Asignar permiso al grupo SECPLA
        secpla_group.permissions.add(block_perm)
        secpla_group.save()
        print("Permiso 'can_block_user' asignado al grupo SECPLA.")
    except Permission.DoesNotExist:
        print("ERROR: Permiso 'can_block_user' no encontrado. Verifica que esté creado y migrado.")

if __name__ == "__main__":
    create_groups_and_assign_permissions()
