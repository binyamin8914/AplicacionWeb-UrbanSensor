# core/context_processors.py
from registration.models import Profile

def group_name(request):
    """
    Devuelve el nombre del grupo del usuario logueado
    para que esté disponible en todos los templates como 'group_name'.
    """
    if not request.user.is_authenticated:
        return {'group_name': None}

    try:
        profile = Profile.objects.get(user=request.user)
        name = profile.group.name
    except Profile.DoesNotExist:
        name = None
    except Exception:
        name = None

    return {'group_name': name}
