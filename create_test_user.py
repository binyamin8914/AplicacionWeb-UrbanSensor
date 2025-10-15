import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UrbanSensor.settings')  # Cambia por el nombre al de tu proyecto x.settings
django.setup()

from django.contrib.auth.models import User, Group
from registration.models import Profile

def create_test_users():
    usuarios = [
        {'username': 'secpla_user2', 'password': 'pass_secpla1234', 'email': 'secpla2@mail.com', 'group': 'SECPLA', 'telefono': '6666-6666'},
        {'username': 'territorial_user2', 'password': 'pass_territorial1234', 'email': 'territorial2@mail.com', 'group': 'Territorial', 'telefono': '7777-7777'},
        {'username': 'direccion_user2', 'password': 'pass_direccion1234', 'email': 'direccion2@mail.com', 'group': 'Direccion', 'telefono': '8888-8888'},
        {'username': 'departamento_user2', 'password': 'pass_departamento1234', 'email': 'departamento2@mail.com', 'group': 'Departamento', 'telefono': '9999-9999'},
        {'username': 'cuadrilla_user2', 'password': 'pass_cuadrilla1234', 'email': 'cuadrilla2@mail.com', 'group': 'Cuadrilla', 'telefono': '0000-0000'}
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
