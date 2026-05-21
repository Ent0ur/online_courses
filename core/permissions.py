from functools import wraps

def role_required(*allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(user_role, *args, **kwargs):
            if user_role in allowed_roles:
                return func(*args, **kwargs)
            else:
                raise PermissionError("У вас недостаточно прав")
        return wrapper
    return decorator