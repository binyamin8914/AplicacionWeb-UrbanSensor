import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UrbanSensor.settings')  # Cambia por el nombre al de tu proyecto x.settings
django.setup()

from django.contrib.auth.models import User, Group
from registration.models import Profile

def build_usuarios():
    usuarios = []

    # SECPLA: secpla_user1..secpla_user2..secpla_user3
    for i in range(1, 4):
        usuarios.append({
            'username': f'secpla_user{i}',
            'password': f'pass_secpla{i}',
            'email': f'secpla{i}@mail.com',
            'group': 'SECPLA',
            'telefono': f'1111-{i}{i}{i}{i}',
            'first_name': f'SecplaName{i}',
            'last_name': f'SecplaSurname{i}'
        })

    # Territorial: territorial_user1..territorial_user2
    for i in range(1, 4):
        usuarios.append({
            'username': f'territorial_user{i}',
            'password': f'pass_territorial{i}',
            'email': f'territorial{i}@mail.com',
            'group': 'Territorial',
            'telefono': f'2222-{i}{i}{i}{i}',
            'first_name': f'TerritorialName{i}',
            'last_name': f'TerritorialSurname{i}'
        })

    # Direccion: direccion_user1..direccion_user9 (suficientes para varias direcciones)
    for i in range(1, 10):
        usuarios.append({
            'username': f'direccion_user{i}',
            'password': f'pass_direccion{i}',
            'email': f'direccion{i}@mail.com',
            'group': 'Direccion',
            'telefono': f'3333-{i:04d}',
            'first_name': f'DireccionName{i}',
            'last_name': f'DireccionSurname{i}'
        })

    # Departamento: departamento_user1..departamento_user11
    for i in range(1, 12):
        usuarios.append({
            'username': f'departamento_user{i}',
            'password': f'pass_departamento{i}',
            'email': f'departamento{i}@mail.com',
            'group': 'Departamento',
            'telefono': f'4444-{i:04d}',
            'first_name': f'DepartamentoName{i}',
            'last_name': f'DepartamentoSurname{i}'
        })

    # Cuadrilla: cuadrilla_user1..cuadrilla_user21
    for i in range(1, 22):
        usuarios.append({
            'username': f'cuadrilla_user{i}',
            'password': f'pass_cuadrilla{i}',
            'email': f'cuadrilla{i}@mail.com',
            'group': 'Cuadrilla',
            'telefono': f'5555-{i:04d}',
            'first_name': f'CuadrillaName{i}',
            'last_name': f'CuadrillaSurname{i}'
        })

    return usuarios

def create_test_users():
    usuarios = build_usuarios()

    for user_data in usuarios:
        # Crea usuario base o lo recupera
        user, created = User.objects.get_or_create(username=user_data['username'], defaults={
            'email': user_data['email'],
            'first_name': user_data.get('first_name', ''),
            'last_name': user_data.get('last_name', ''),
            'is_active': True,
        })
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"Usuario '{user.username}' creado.")
        else:
<<<<<<< HEAD
            # Actualiza datos básicos si cambiaron
            updated = False
            if user.email != user_data['email']:
                user.email = user_data['email']
                updated = True
            if user.first_name != user_data.get('first_name', ''):
                user.first_name = user_data.get('first_name', '')
                updated = True
            if user.last_name != user_data.get('last_name', ''):
                user.last_name = user_data.get('last_name', '')
                updated = True
            if updated:
                user.save()
                print(f"Usuario '{user.username}' actualizado.")
            else:
                print(f"Usuario '{user.username}' ya existe.")

        # Asigna grupo (asume que el Group ya existe)
        try:
            group = Group.objects.get(name=user_data['group'])
        except Group.DoesNotExist:
            # Si el grupo no existe, lo creamos para evitar errores
            group = Group.objects.create(name=user_data['group'])
            print(f"Grupo '{group.name}' creado automáticamente.")

=======
            print(f"Usuario '{user.username}' ya existe.")

        # Asigna grupo
        group = Group.objects.get(name=user_data['group'])
>>>>>>> dd07e64c90885b997006adea9d8508f590459c99
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

<<<<<<< HEAD
        print(f"Usuario '{user.username}' asignado al grupo '{group.name}' con teléfono '{user_data['telefono']}'.")
=======
        print(f"Usuario '{user.username}' asignado al grupo '{group.name}'.")
>>>>>>> dd07e64c90885b997006adea9d8508f590459c99

if __name__ == "__main__":
    create_test_users()
