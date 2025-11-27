import os
import django
from django.db import transaction


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UrbanSensor.settings')
django.setup()

from django.contrib.auth.models import User
from direcciones.models import Direccion
from departamentos.models import Departamento
from cuadrillas.models import Cuadrilla



from django.db import transaction, IntegrityError

def find_alternative_user(prefix, model_check, start=1, max_try=200):
    """
    Busca un usuario disponible con username f'{prefix}{i}' que NO esté asignado
    como encargado en el modelo model_check (p. ej. Departamento, Cuadrilla).
    Devuelve User o None.
    """
    for i in range(start, start + max_try):
        uname = f"{prefix}{i}"
        u = User.objects.filter(username=uname).first()
        if not u:
            continue
       
        if not model_check.objects.filter(encargado=u).exists():
            return u
    return None

def create_direcciones(direcciones):
    for d in direcciones:
        username = d.get('encargado_username')
        encargado = None
        if username:
            encargado = User.objects.filter(username=username).first()
            if not encargado:
                print(f"[SKIP] Direccion '{d['nombre']}': usuario encargado '{username}' no existe.")
                continue
            
            if Direccion.objects.filter(encargado=encargado).exists():
                alt = find_alternative_user('direccion_user', Direccion, start=1)
                if alt:
                    print(f"[WARN] Usuario '{username}' ya es encargado de otra Direcci ón. Usando '{alt.username}' en su lugar.")
                    encargado = alt
                else:
                    print(f"[SKIP] Direccion '{d['nombre']}': no hay usuarios 'direccion_userN' libres para asignar.")
                    continue

        try:
            obj, created = Direccion.objects.update_or_create(
                nombre=d['nombre'],
                defaults={
                    'encargado': encargado,
                    'esta_activa': d.get('esta_activa', True)
                }
            )
            action = "Creada" if created else "Actualizada"
            print(f"[{action}] Direccion: {obj.nombre} (encargado: {encargado.username if encargado else 'None'})")
        except IntegrityError as e:
            print(f"[ERROR] Al crear/actualizar Direccion '{d['nombre']}': {e}")

def create_departamentos(departamentos):
    for dep in departamentos:
        direccion_nombre = dep.get('direccion_nombre')
        try:
            direccion = Direccion.objects.get(nombre=direccion_nombre)
        except Direccion.DoesNotExist:
            print(f"[SKIP] Departamento '{dep['nombre']}': Direccion '{direccion_nombre}' no encontrada.")
            continue

        username = dep.get('encargado_username')
        encargado = None
        if username:
            encargado = User.objects.filter(username=username).first()
            if not encargado:
                print(f"[SKIP] Departamento '{dep['nombre']}': usuario encargado '{username}' no existe.")
                continue

            
            existing = Departamento.objects.filter(encargado=encargado).exclude(nombre=dep['nombre']).first()
            if existing:
                
                alt = find_alternative_user('departamento_user', Departamento, start=1)
                if alt:
                    print(f"[WARN] Usuario '{username}' ya está encargado de '{existing.nombre}'. Usando '{alt.username}' como encargado para '{dep['nombre']}'.")
                    encargado = alt
                else:
                    print(f"[SKIP] Departamento '{dep['nombre']}': encargado '{username}' ya está asignado y no hay alternativas disponibles.")
                    continue

        try:
            obj, created = Departamento.objects.update_or_create(
                nombre=dep['nombre'],
                defaults={
                    'encargado': encargado,
                    'direccion': direccion,
                    'esta_activo': dep.get('esta_activo', True)
                }
            )
            action = "Creado" if created else "Actualizado"
            print(f"[{action}] Departamento: {obj.nombre} (direccion: {direccion_nombre}, encargado: {encargado.username if encargado else 'None'})")
        except IntegrityError as e:
            print(f"[ERROR] Al crear/actualizar Departamento '{dep['nombre']}': {e}")

def create_cuadrillas(cuadrillas):
    for c in cuadrillas:
        departamento_nombre = c.get('departamento_nombre')
        try:
            departamento = Departamento.objects.get(nombre=departamento_nombre)
        except Departamento.DoesNotExist:
            print(f"[SKIP] Cuadrilla '{c['nombre']}': Departamento '{departamento_nombre}' no encontrado.")
            continue

        username = c.get('encargado_username')
        encargado = None
        if username:
            encargado = User.objects.filter(username=username).first()
            if not encargado:
                print(f"[SKIP] Cuadrilla '{c['nombre']}': usuario encargado '{username}' no existe.")
                continue

            
            existing = Cuadrilla.objects.filter(encargado=encargado).exclude(nombre=c['nombre']).first()
            if existing:
                alt = find_alternative_user('cuadrilla_user', Cuadrilla, start=1)
                if alt:
                    print(f"[WARN] Usuario '{username}' ya está encargado de '{existing.nombre}'. Usando '{alt.username}' para '{c['nombre']}'.")
                    encargado = alt
                else:
                    print(f"[SKIP] Cuadrilla '{c['nombre']}': encargado '{username}' ya está asignado y no hay alternativas disponibles.")
                    continue

        try:
            obj, created = Cuadrilla.objects.update_or_create(
                nombre=c['nombre'],
                defaults={
                    'encargado': encargado,
                    'departamento': departamento,
                    'esta_activa': c.get('esta_activa', True)
                }
            )
            action = "Creada" if created else "Actualizada"
            print(f"[{action}] Cuadrilla: {obj.nombre} (departamento: {departamento_nombre}, encargado: {encargado.username if encargado else 'None'})")
        except IntegrityError as e:
            print(f"[ERROR] Al crear/actualizar Cuadrilla '{c['nombre']}': {e}")

def create_all():
    
    direcciones = [
        {'nombre': 'Direccion de Obras', 'encargado_username': 'direccion_user1', 'esta_activa': True},
        {'nombre': 'Direccion de Medio Ambiente', 'encargado_username': 'direccion_user2', 'esta_activa': True},
        {'nombre': 'Direccion de Salud', 'encargado_username': 'direccion_user3', 'esta_activa': True},
        {'nombre': 'Direccion de Transporte', 'encargado_username': 'direccion_user4', 'esta_activa': True},
        {'nombre': 'Direccion de Cultura', 'encargado_username': 'direccion_user5', 'esta_activa': True},
        {'nombre': 'Direccion de Seguridad', 'encargado_username': 'direccion_user6', 'esta_activa': True},
        {'nombre': 'Direccion de Desarrollo Urbano', 'encargado_username': 'direccion_user7', 'esta_activa': True},
        {'nombre': 'Direccion de Parques y Jardines', 'encargado_username': 'direccion_user8', 'esta_activa': True},
    ]

    departamentos = [
        {'nombre': 'Departamento de Vialidad', 'encargado_username': 'departamento_user1', 'direccion_nombre': 'Direccion de Obras', 'esta_activo': True},
        {'nombre': 'Departamento de Recoleccion', 'encargado_username': 'departamento_user2', 'direccion_nombre': 'Direccion de Medio Ambiente', 'esta_activo': True},
        {'nombre': 'Departamento de Epidemiologia', 'encargado_username': 'departamento_user3', 'direccion_nombre': 'Direccion de Salud', 'esta_activo': True},
        {'nombre': 'Departamento de Señalizacion', 'encargado_username': 'departamento_user4', 'direccion_nombre': 'Direccion de Transporte', 'esta_activo': True},
        {'nombre': 'Departamento de Patrimonio', 'encargado_username': 'departamento_user5', 'direccion_nombre': 'Direccion de Cultura', 'esta_activo': True},
        {'nombre': 'Departamento de Prevencion', 'encargado_username': 'departamento_user6', 'direccion_nombre': 'Direccion de Seguridad', 'esta_activo': True},
        {'nombre': 'Departamento de Planificacion', 'encargado_username': 'departamento_user7', 'direccion_nombre': 'Direccion de Desarrollo Urbano', 'esta_activo': True},
        {'nombre': 'Departamento de Mantenimiento de Parques', 'encargado_username': 'departamento_user8', 'direccion_nombre': 'Direccion de Parques y Jardines', 'esta_activo': True},
        {'nombre': 'Departamento de Alumbrado', 'encargado_username': 'departamento_user9', 'direccion_nombre': 'Direccion de Obras', 'esta_activo': True},
        {'nombre': 'Departamento de Limpieza', 'encargado_username': 'departamento_user10', 'direccion_nombre': 'Direccion de Medio Ambiente', 'esta_activo': True},
    ]

    cuadrillas = [
        {'nombre': 'Cuadrilla 1 - Vialidad Norte', 'encargado_username': 'cuadrilla_user1', 'departamento_nombre': 'Departamento de Vialidad', 'esta_activa': True},
        {'nombre': 'Cuadrilla 2 - Vialidad Sur', 'encargado_username': 'cuadrilla_user2', 'departamento_nombre': 'Departamento de Vialidad', 'esta_activa': True},
        {'nombre': 'Cuadrilla 3 - Recoleccion Central', 'encargado_username': 'cuadrilla_user3', 'departamento_nombre': 'Departamento de Recoleccion', 'esta_activa': True},
        {'nombre': 'Cuadrilla 4 - Recoleccion Oeste', 'encargado_username': 'cuadrilla_user4', 'departamento_nombre': 'Departamento de Recoleccion', 'esta_activa': True},
        {'nombre': 'Cuadrilla 5 - Epidemiologia Zona 1', 'encargado_username': 'cuadrilla_user5', 'departamento_nombre': 'Departamento de Epidemiologia', 'esta_activa': True},
        {'nombre': 'Cuadrilla 6 - Señalizacion Express', 'encargado_username': 'cuadrilla_user6', 'departamento_nombre': 'Departamento de Señalizacion', 'esta_activa': True},
        {'nombre': 'Cuadrilla 7 - Patrimonio Centro', 'encargado_username': 'cuadrilla_user7', 'departamento_nombre': 'Departamento de Patrimonio', 'esta_activa': True},
        {'nombre': 'Cuadrilla 8 - Prevencion Movil', 'encargado_username': 'cuadrilla_user8', 'departamento_nombre': 'Departamento de Prevencion', 'esta_activa': True},
        {'nombre': 'Cuadrilla 9 - Planificacion Campo', 'encargado_username': 'cuadrilla_user9', 'departamento_nombre': 'Departamento de Planificacion', 'esta_activa': True},
        {'nombre': 'Cuadrilla 10 - Parques Norte', 'encargado_username': 'cuadrilla_user10', 'departamento_nombre': 'Departamento de Mantenimiento de Parques', 'esta_activa': True},
        {'nombre': 'Cuadrilla 11 - Alumbrado Este', 'encargado_username': 'cuadrilla_user11', 'departamento_nombre': 'Departamento de Alumbrado', 'esta_activa': True},
        {'nombre': 'Cuadrilla 12 - Limpieza Express', 'encargado_username': 'cuadrilla_user12', 'departamento_nombre': 'Departamento de Limpieza', 'esta_activa': True},
        {'nombre': 'Cuadrilla 13 - Vialidad Rapid', 'encargado_username': 'cuadrilla_user13', 'departamento_nombre': 'Departamento de Vialidad', 'esta_activa': True},
        {'nombre': 'Cuadrilla 14 - Recoleccion Nocturna', 'encargado_username': 'cuadrilla_user14', 'departamento_nombre': 'Departamento de Recoleccion', 'esta_activa': True},
        {'nombre': 'Cuadrilla 15 - Salud Movil', 'encargado_username': 'cuadrilla_user15', 'departamento_nombre': 'Departamento de Epidemiologia', 'esta_activa': True},
        {'nombre': 'Cuadrilla 16 - Señalizacion Sur', 'encargado_username': 'cuadrilla_user16', 'departamento_nombre': 'Departamento de Señalizacion', 'esta_activa': True},
        {'nombre': 'Cuadrilla 17 - Parques Sur', 'encargado_username': 'cuadrilla_user17', 'departamento_nombre': 'Departamento de Mantenimiento de Parques', 'esta_activa': True},
        {'nombre': 'Cuadrilla 18 - Prevencion Fija', 'encargado_username': 'cuadrilla_user18', 'departamento_nombre': 'Departamento de Prevencion', 'esta_activa': True},
        {'nombre': 'Cuadrilla 19 - Planificacion Centro', 'encargado_username': 'cuadrilla_user19', 'departamento_nombre': 'Departamento de Planificacion', 'esta_activa': True},
        {'nombre': 'Cuadrilla 20 - Servicios Generales', 'encargado_username': 'cuadrilla_user20', 'departamento_nombre': 'Departamento de Limpieza', 'esta_activa': True},
    ]

    
    with transaction.atomic():
        create_direcciones(direcciones)
        create_departamentos(departamentos)
        create_cuadrillas(cuadrillas)

if __name__ == "__main__":
    create_all()