import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UrbanSensor.settings')  # Cambia por el nombre al de tu proyecto x.settings
django.setup()

from django.contrib.auth.models import User, Group
from registration.models import Profile

def create_test_users():
    usuarios = [
        {'username': 'secpla_user', 'password': 'pass_secpla123', 'email': 'secpla@mail.com', 'group': 'SECPLA', 'telefono': '1111-1111'},
        {'username': 'territorial_user', 'password': 'pass_territorial123', 'email': 'territorial@mail.com', 'group': 'Territorial', 'telefono': '2222-2222'},
        {'username': 'direccion_user', 'password': 'pass_direccion123', 'email': 'direccion@mail.com', 'group': 'Direccion', 'telefono': '3333-3333'},
        {'username': 'departamento_user', 'password': 'pass_departamento123', 'email': 'departamento@mail.com', 'group': 'Departamento', 'telefono': '4444-4444'},
        {'username': 'cuadrilla_user', 'password': 'pass_cuadrilla123', 'email': 'cuadrilla@mail.com', 'group': 'Cuadrilla', 'telefono': '5555-5555'}
    ]

    for user_data in usuarios:
        # Crea usuario base
        user, created = User.objects.get_or_create(username=user_data['username'], defaults={
            'email': user_data['email']
        })
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"Usuario '{user.username}' creado.")
        else:
            print(f"Usuario '{user.username}' ya existe.")

        # Asigna grupo
        group = Group.objects.get(name=user_data['group'])
        user.groups.clear()
        user.groups.add(group)
        user.save()

        # Crea o actualiza perfil extendido
        profile, prof_created = Profile.objects.get_or_create(user=user, defaults={
            'group': group,
            'telefono': user_data['telefono']
        })
        if not prof_created:
            profile.group = group
            profile.telefono = user_data['telefono']
            profile.save()

        print(f"Usuario '{user.username}' asignado al grupo '{group.name}'.")

if __name__ == "__main__":
    create_test_users()
