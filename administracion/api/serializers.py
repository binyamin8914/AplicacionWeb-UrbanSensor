from django.contrib.auth import get_user_model
from rest_framework import serializers
from registration.models import Profile
from django.contrib.auth.models import Group
from direcciones.models import Direccion

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    group = serializers.CharField(source='group.name')  # Cambiado para devolver solo el nombre
    direccion = serializers.PrimaryKeyRelatedField(
        queryset=Direccion.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Profile
        fields = ('group', 'telefono', 'direccion')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)
    password = serializers.CharField(write_only=True, required=False)  # Agregado

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'email', 'is_active', 'profile', 'password'
        )

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)
        
        user = User.objects.create(**validated_data)
        
        # Establecer contraseña de forma segura
        if password:
            user.set_password(password)
            user.save()

        if profile_data:
            # Obtener el grupo por nombre
            group_name = profile_data.pop('group', {}).get('name')
            if group_name:
                group = Group.objects.get(name=group_name)
                Profile.objects.create(user=user, group=group, **profile_data)
            else:
                Profile.objects.create(user=user, **profile_data)

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)

        # Actualizar datos de usuario
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Actualizar contraseña si se proporciona
        if password:
            instance.set_password(password)
        
        instance.save()

        # Actualizar perfil
        if profile_data:
            group_name = profile_data.pop('group', {}).get('name')
            if group_name:
                group = Group.objects.get(name=group_name)
                profile_data['group'] = group
            
            Profile.objects.update_or_create(
                user=instance,
                defaults=profile_data
            )

        return instance


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


# El DireccionSerializer debería estar en direcciones/serializers.py
# Si no existe ese archivo, créalo con:
# from rest_framework import serializers
# from .models import Direccion
#
# class DireccionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Direccion
#         fields = '__all__'