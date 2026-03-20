# BlogReddit API

API REST estilo Reddit construida con Django y Django REST Framework.

---

## Tabla de contenidos

- [Stack tecnológico](#stack-tecnológico)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Estado actual](#estado-actual)
- [Plan de desarrollo](#plan-de-desarrollo)
- [Instalación](#instalación)
- [Variables de entorno](#variables-de-entorno)

---

## Stack tecnológico

| Herramienta | Versión | Para qué sirve |
|---|---|---|
| Python | 3.12+ | Lenguaje base |
| Django | 6.0 | Framework web |
| Django REST Framework | 3.17 | Construir la API |
| djangorestframework-simplejwt | 5.x | Autenticación con tokens JWT |
| MySQL | 8.x | Base de datos |
| python-decouple | 3.x | Variables de entorno |
| Pillow | latest | Manejo de imágenes (avatars) |
| drf-spectacular | latest | Documentación Swagger automática |

---

## Estructura del proyecto

```
blogreddit/
├── config/
│   ├── settings/
│   │   ├── base.py       # Configuración compartida
│   │   └── local.py      # Configuración solo para desarrollo
│   ├── urls.py           # URLs principales
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── users/            # Registro, login, perfil
│   ├── posts/            # Posts, categorías, votos en posts
│   └── comments/         # Comentarios anidados, votos en comentarios
├── manage.py
├── requirements.txt
└── .env                  # Nunca subir al repositorio
```

---

## Estado actual

- [x] Fase 1 — Estructura del proyecto, MySQL, DRF, modelo User personalizado
- [x] Fase 2 — Autenticación JWT completa (registro, login, refresh, perfil)
- [x] Fase 3 — CRUD Posts con filtros, búsqueda y ordenamiento
- [x] Fase 4 — Comentarios en posts (anidados opcionales)
- [x] Fase 5 — Sistema de votos con toggle (up/down por post)
- [x] Fase 6 — Roles (user / moderator / admin), panel Admin profesional
- [x] Fase 7 — Throttling, Swagger docs, tests, manejo de errores, CORS para frontend

---

## Plan de desarrollo

> Cada paso tiene exactamente lo que hay que hacer y en qué orden.
> No pases al siguiente paso hasta tener el actual funcionando.

---

### FASE 1 — Fundamentos ✅ Completada

La estructura base ya está creada. Tienes:
- Proyecto Django con settings dividido en `base.py` y `local.py`
- MySQL configurado
- DRF instalado
- Modelo `User` personalizado con avatar, bio y karma

**Pendiente de esta fase:**
1. Asegurarte de que `.env` tiene todas las credenciales y no están hardcodeadas en `settings`
2. Correr las migraciones iniciales:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

---

### FASE 2 — Autenticación y usuarios

**Objetivo:** Los usuarios pueden registrarse, hacer login, obtener un token JWT y manejar su perfil.

**Orden de implementación:**

**Paso 1 — Configurar JWT en settings**
En `config/settings/base.py` agregar:
```python
from datetime import timedelta

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

**Paso 2 — Crear `apps/users/serializers.py`**
- `UserSerializer` — para leer/actualizar perfil
- `RegisterSerializer` — para registro (con validación de contraseña repetida)

**Paso 3 — Crear `apps/users/views.py`**
- `RegisterView` — `CreateAPIView`, sin autenticación requerida
- `ProfileView` — `RetrieveUpdateAPIView`, requiere estar logueado
- `ChangePasswordView` — requiere estar logueado

**Paso 4 — Crear `apps/users/urls.py`**
```
POST   /api/users/register/
GET    /api/users/me/
PUT    /api/users/me/
POST   /api/users/change-password/
```

**Paso 5 — Conectar JWT en `config/urls.py`**
```
POST   /api/auth/token/          → obtener access + refresh token
POST   /api/auth/token/refresh/  → renovar el access token
```

**Paso 6 — Registrar User en `apps/users/admin.py`**

**Paso 7 — Probar con Postman o httpie:**
- Registrar usuario → login → obtener token → acceder a `/me/` con Bearer token

---

### FASE 3 — Posts

**Objetivo:** CRUD completo de posts con categorías y permisos.

**Paso 1 — Modelo `Category`** en `apps/posts/models.py`
```python
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
```

**Paso 2 — Actualizar modelo `Post`**
- Agregar FK a `Category`
- Agregar campo `slug` (generado automático desde el título)

**Paso 3 — Crear `apps/posts/serializers.py`**
- `CategorySerializer`
- `PostSerializer` — muestra nombre del autor, categoría, score (upvotes - downvotes)
- `PostCreateSerializer` — para crear/editar (el autor se asigna automáticamente)

**Paso 4 — Crear permiso personalizado `IsAuthorOrReadOnly`**
```python
# apps/posts/permissions.py
class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
```

**Paso 5 — Crear `apps/posts/views.py`**
- `CategoryViewSet` — solo admins pueden crear/editar categorías
- `PostViewSet` — CRUD con el permiso `IsAuthorOrReadOnly`

**Paso 6 — Crear `apps/posts/urls.py`** con `DefaultRouter`

**Paso 7 — Makemigrations + migrate**

**Paso 8 — Probar:**
- Crear post sin token → debe dar 401
- Crear post con token → debe funcionar
- Editar post de otro usuario → debe dar 403

---

### FASE 4 — Comentarios

**Objetivo:** Comentarios en posts con respuestas anidadas.

**Paso 1 — Modelo `Comment`** en `apps/comments/models.py`
```python
class Comment(models.Model):
    post    = ForeignKey('posts.Post', related_name='comments')
    author  = ForeignKey(settings.AUTH_USER_MODEL, related_name='comments')
    parent  = ForeignKey('self', null=True, blank=True, related_name='replies')
    content = TextField()
    created_at / updated_at
```
El campo `parent` es la clave: si es null, es comentario raíz. Si tiene valor, es una respuesta.

**Paso 2 — Serializer con anidamiento**
- `CommentSerializer` que incluye `replies` (un nivel de profundidad para evitar recursión infinita)

**Paso 3 — `CommentViewSet`**
- `get_queryset` filtra por `post` (query param `?post=1`)
- Solo devuelve comentarios raíz (sin parent) en el listado — las respuestas vienen anidadas

**Paso 4 — URLs y conectar**

**Paso 5 — Probar:**
- Crear comentario en un post
- Responder a ese comentario (usando `parent=<id>`)
- Ver que las respuestas aparecen anidadas en el JSON

---

### FASE 5 — Sistema de votos

**Objetivo:** Up/downvote en posts y comentarios. Un usuario = un voto por ítem.

**Paso 1 — Modelo `Vote`** en `apps/posts/models.py`
```python
class Vote(models.Model):
    UPVOTE = 'up'
    DOWNVOTE = 'down'
    user      = ForeignKey(User)
    post      = ForeignKey(Post)
    vote_type = CharField(choices=[('up', 'Up'), ('down', 'Down')])

    class Meta:
        unique_together = ('user', 'post')  # evita votos duplicados
```

**Paso 2 — Lógica de votación (en el ViewSet):**
```
Si el usuario NO ha votado    → crear voto, incrementar contador
Si el usuario ya votó igual   → eliminar voto, decrementar contador (toggle)
Si el usuario votó diferente  → cambiar tipo, actualizar ambos contadores
```

**Paso 3 — Acción personalizada en `PostViewSet`**
```python
@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
def vote(self, request, pk=None):
    ...
```

**Paso 4 — Repetir para comentarios** con un modelo `CommentVote`

**Paso 5 — Probar:**
- Votar dos veces seguidas → debe cancelar el voto
- Votar up y luego down → debe cambiar

---

### FASE 6 — Roles y administración

**Objetivo:** Sistema de roles con diferentes niveles de permisos.

**Paso 1 — Agregar campo `role` al modelo User**
```python
class User(AbstractUser):
    ROLES = [
        ('user', 'Usuario'),
        ('moderator', 'Moderador'),
        ('admin', 'Administrador'),
    ]
    role = models.CharField(max_length=20, choices=ROLES, default='user')
```

**Paso 2 — Permisos por rol**
```python
class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['moderator', 'admin']

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'
```

**Paso 3 — Aplicar permisos:**
- Admin y moderadores pueden borrar cualquier post/comentario
- Solo admins pueden crear categorías
- Solo admins pueden cambiar el rol de otros usuarios

**Paso 4 — Configurar Django Admin profesionalmente**
```python
# apps/users/admin.py
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'karma', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email']
```

**Paso 5 — Crear superusuario y probar el panel admin**
```bash
python manage.py createsuperuser
```

---

### FASE 7 — Calidad profesional

**Objetivo:** El proyecto queda listo para mostrarlo en un portfolio o entrevista.

**Paso 1 — Manejo centralizado de errores**
Crear handler personalizado en `config/exceptions.py` que devuelva siempre el mismo formato JSON:
```json
{
  "error": "mensaje de error",
  "detail": { ... }
}
```

**Paso 2 — Throttling (límite de peticiones)**
En `REST_FRAMEWORK` de settings:
```python
'DEFAULT_THROTTLE_CLASSES': [
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle',
],
'DEFAULT_THROTTLE_RATES': {
    'anon': '100/day',
    'user': '1000/day',
},
```

**Paso 3 — Filtros, búsqueda y ordenamiento**
Instalar `django-filter` y configurar en los ViewSets:
```python
filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
filterset_fields = ['category']
search_fields = ['title', 'content']
ordering_fields = ['created_at', 'upvotes']
```

**Paso 4 — Documentación con Swagger**
Instalar `drf-spectacular`:
```bash
pip install drf-spectacular
```
Agregar a `config/urls.py`:
```
GET /api/schema/        → OpenAPI schema
GET /api/docs/          → Swagger UI interactivo
```

**Paso 5 — Tests**
Para cada app, escribir en `tests.py`:
- Test de registro de usuario
- Test de login y token
- Test de crear post (con y sin autenticación)
- Test de votar
- Test de permisos (editar post ajeno → 403)

Correr tests:
```bash
python manage.py test apps
```

---

## Instalación

```bash
# 1. Clonar y entrar al proyecto
cd blogreddit

# 2. Activar entorno virtual
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
# Copiar .env.example a .env y rellenar con tus datos

# 5. Crear la base de datos en MySQL
mysql -u root -p
CREATE DATABASE blogreddit CHARACTER SET utf8mb4;
exit;

# 6. Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# 7. Crear superusuario
python manage.py createsuperuser

# 8. Correr el servidor
python manage.py runserver
```

---

## Variables de entorno

Crear archivo `.env` en la raíz del proyecto (nunca subir a git):

```env
SECRET_KEY=genera-una-clave-segura-aqui
DEBUG=True
DB_NAME=blogreddit
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=3306
```

---

## Endpoints (referencia rápida)

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/api/auth/token/` | No | Login → obtener tokens |
| POST | `/api/auth/token/refresh/` | No | Renovar access token |
| POST | `/api/users/register/` | No | Crear cuenta |
| GET/PUT | `/api/users/me/` | Sí | Ver/editar mi perfil |
| POST | `/api/users/change-password/` | Sí | Cambiar contraseña |
| GET | `/api/posts/` | No | Listar posts |
| POST | `/api/posts/` | Sí | Crear post |
| GET/PUT/DELETE | `/api/posts/{id}/` | Parcial | Ver/editar/borrar post |
| POST | `/api/posts/{id}/vote/` | Sí | Votar post |
| GET | `/api/comments/?post={id}` | No | Comentarios de un post |
| POST | `/api/comments/` | Sí | Crear comentario |
| GET/PUT/DELETE | `/api/comments/{id}/` | Parcial | Ver/editar/borrar comentario |
| GET | `/api/docs/` | No | Swagger UI |
