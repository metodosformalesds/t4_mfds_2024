from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    """
    Clase implementada por Alan
    Backend de autenticación personalizado basado en correo electrónico.

    Este backend permite a los usuarios autenticarse utilizando su dirección de correo electrónico
    en lugar del nombre de usuario predeterminado de Django. También proporciona un método para obtener
    un usuario por su ID.

    Métodos:
        authenticate(request, username=None, password=None, **kwargs):
            Autentica al usuario utilizando su correo electrónico y contraseña.
        get_user(user_id):
            Recupera un usuario por su ID.

    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Funcion implementada por Alan
        Autentica a un usuario mediante correo electrónico y contraseña.

        Este método intenta encontrar un usuario con la dirección de correo electrónico proporcionada.
        Si el usuario existe y la contraseña es válida, devuelve la instancia del usuario.
        De lo contrario, devuelve `None`.

        Args:
            request (HttpRequest): El objeto de la solicitud HTTP (puede ser `None` en algunos casos).
            username (str): El correo electrónico del usuario.
            password (str): La contraseña del usuario.
            **kwargs: Argumentos adicionales.

        Returns:
            User: La instancia del usuario autenticado, o `None` si las credenciales son incorrectas.
        """
        User = get_user_model()
        try:
            # Intenta buscar al usuario por email
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        # Verifica si la contraseña es correcta
        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        """
        Funcion implementada por Alan
        Recupera un usuario por su ID.

        Este método busca un usuario en la base de datos utilizando su ID. Si el usuario no existe,
        devuelve `None`.

        Args:
            user_id (int): El ID del usuario que se quiere recuperar.

        Returns:
            User: La instancia del usuario si existe, o `None` si no se encuentra.
        """
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None