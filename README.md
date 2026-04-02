# ONYX BLOG — DECAY–84 EDITION

> A brutalist full-stack community platform for ideas, discourse, and leaving your mark on the wall.

---

## Live Demo

| Service | URL |
|---------|-----|
| Frontend (Vercel) | `https://blogreddit-frontend-an47.vercel.app` |
| Backend API (Render) | `https://blogreddit-api.onrender.com` |
| API Docs (Swagger) | `https://blogreddit-api.onrender.com/api/docs/` |
| Django Admin | `https://blogreddit-api.onrender.com/admin/` |

---

## Stack

### Backend
| Herramienta | Versión | Uso |
|---|---|---|
| Python | 3.12+ | Lenguaje base |
| Django | 5.x | Framework web |
| Django REST Framework | 3.17 | API REST |
| djangorestframework-simplejwt | 5.x | Auth JWT con blacklist y rotación |
| PostgreSQL (Neon) | 17 | Base de datos en producción |
| python-decouple | 3.x | Variables de entorno |
| Pillow | latest | Procesamiento de imágenes |
| drf-spectacular | latest | Docs Swagger automáticas |
| Gunicorn + WhiteNoise | latest | Servidor producción + archivos estáticos |

### Frontend
| Herramienta | Versión | Uso |
|---|---|---|
| React | 18 | UI |
| Vite | 5 | Build tool |
| React Router v6 | 6 | Routing con `location.state` |
| TanStack Query | 5 | Server state / caché |
| Axios | latest | HTTP client con interceptores JWT |
| react-easy-crop | latest | Crop circular de avatares |
| DOMPurify | latest | Sanitización XSS en markdown |

---

## Estructura del proyecto

```
Blog-Claude/
├── blogreddit/                  # Backend Django
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py          # Configuración compartida
│   │   │   ├── local.py         # Desarrollo local
│   │   │   └── production.py    # Producción (Render)
│   │   ├── urls.py              # URLs raíz
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── users/               # Registro, perfil, roles, perfiles públicos
│   │   │   ├── models.py        # User con avatar (base64), bio, karma, role
│   │   │   ├── views.py         # ProfileView, PublicProfileView, RegisterView
│   │   │   ├── serializers.py   # UserSerializer, PublicUserSerializer, UserCommentSerializer
│   │   │   └── urls.py
│   │   ├── posts/               # Posts, comentarios, votos, admin API
│   │   │   ├── models.py        # Post, Comment, Vote
│   │   │   ├── views.py         # CRUD posts/comentarios, VoteView, Admin views
│   │   │   ├── serializers.py   # PostSerializer, CommentSerializer, AdminCommentSerializer
│   │   │   ├── permissions.py   # IsAuthorOrReadOnly, IsAdminRole
│   │   │   ├── urls.py
│   │   │   └── admin_urls.py    # /api/admin/* rutas
│   │   └── comments/            # App placeholder
│   ├── manage.py
│   └── requirements.txt
│
└── blogreddit-frontend/         # Frontend React
    ├── src/
    │   ├── pages/
    │   │   ├── Home.jsx          # Feed con búsqueda y sorting
    │   │   ├── AuthPage.jsx      # Login / Registro con tabs
    │   │   ├── CreatePost.jsx    # Editor markdown + imagen
    │   │   ├── PostDetail.jsx    # Post + comentarios + botón back contextual
    │   │   ├── Profile.jsx       # Perfil propio (avatar, bio, settings)
    │   │   ├── PublicProfile.jsx # Perfil público /u/:username (read-only)
    │   │   └── AdminPanel.jsx    # Panel de administración (role=admin)
    │   ├── components/
    │   │   ├── Navbar.jsx        # Logo SVG ONYX, link CMD para admins
    │   │   ├── Footer.jsx        # Logo SVG, links, créditos
    │   │   ├── PostCard.jsx      # Card de post en el feed
    │   │   ├── VoteButtons.jsx   # Up/downvote con toggle
    │   │   ├── AvatarCropModal.jsx # Crop circular con zoom (react-easy-crop)
    │   │   ├── ParticleCanvas.jsx
    │   │   └── GrainOverlay.jsx
    │   ├── context/
    │   │   └── AuthContext.jsx   # JWT state, login/logout, refreshUser
    │   └── api/
    │       └── axios.js          # Interceptores de token y refresh automático
    ├── public/
    │   └── favicon.svg           # Logo ONYX SVG
    └── vercel.json               # Headers de seguridad (CSP, HSTS, etc.)
```

---

## Features

### Autenticación
- Registro y login con JWT
- Access token (30 min) + Refresh token (1 día)
- Rotación automática de refresh tokens
- JWT Blacklist — los tokens invalidados no pueden reutilizarse
- Interceptor de Axios que renueva el access token automáticamente al expirar

### Usuarios y perfiles
- Perfil propio editable: avatar + bio
- **Avatares almacenados como base64 en la DB** (sin servicios externos)
- **Crop modal circular** para ajustar la foto antes de guardarla
- GIFs se bypasean el crop (el canvas rompía la animación)
- Perfiles públicos en `/u/:username` — read-only, misma estética
- Sistema de karma y ranking: RECRUIT → ROOKIE → REGULAR → VETERAN
- Autor y avatar clickeables en PostDetail y comentarios → llevan al perfil público

### Posts y comentarios
- CRUD de posts con imagen opcional (JPEG/PNG/GIF/WEBP, max 5 MB)
- Editor con soporte markdown, sanitizado con DOMPurify (anti-XSS)
- Comentarios en posts
- Sistema de votos up/down con toggle y cambio de sentido
- Búsqueda por título/contenido/autor, ordenamiento por fecha y votos

### Navegación contextual
- Botón **← Back** en PostDetail cambia según de dónde veniste:
  - Feed → `← BACK TO FEED`
  - Perfil propio → `← BACK TO MY PROFILE`
  - Perfil de otro usuario → `← BACK TO [USERNAME]'S PROFILE`
- Implementado con `location.state` de React Router (sin query params)

### Panel de administración
- Accesible en `/admin-panel` solo si `role = admin`
- Estadísticas globales: total posts, comentarios, usuarios
- Listado de todos los posts y comentarios con búsqueda
- Eliminar posts y comentarios individuales
- Guard inteligente: espera a que el perfil cargue antes de verificar el rol
- Botón ⚡ CMD en el navbar solo visible para admins

### Seguridad
- **Rate limiting:** 60 req/hora anónimos, 500 req/hora usuarios, 5/min en login
- **DOMPurify** en el frontend para sanear contenido markdown
- **Security headers** en Vercel: CSP, HSTS, X-Frame-Options: DENY, X-Content-Type-Options
- **JWT Blacklist** con rotación de refresh tokens
- **IsAdminRole** permission class para endpoints admin
- Validación de tipo y tamaño en uploads (avatar y post image)
- Permisos explícitos en todas las vistas

### Diseño
- Estética **neobrutalist** — bordes negros, sombras sólidas, tipografía monoespaciada
- Logo SVG **ONYX** con stroke verde `#7CB342` en navbar, footer y favicon
- Diseño responsivo para móvil (≤860px columna única, tabs con scroll horizontal)

---

## API Endpoints

### Auth
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/api/auth/token/` | No | Login → access + refresh token |
| POST | `/api/auth/token/refresh/` | No | Renovar access token |

### Usuarios
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/api/users/register/` | No | Crear cuenta |
| GET/PATCH | `/api/users/me/` | Sí | Ver/editar mi perfil + avatar |
| GET | `/api/users/me/comments/` | Sí | Mis comentarios |
| GET | `/api/users/:username/` | No | Perfil público |
| GET | `/api/users/:username/comments/` | No | Comentarios públicos del usuario |

### Posts
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/posts/` | No | Listar posts (filtros, búsqueda, orden) |
| POST | `/api/posts/` | Sí | Crear post |
| GET | `/api/posts/:id/` | No | Ver post |
| PUT/PATCH | `/api/posts/:id/` | Sí (autor) | Editar post |
| DELETE | `/api/posts/:id/` | Sí (autor) | Borrar post |
| POST | `/api/posts/:id/vote/` | Sí | Votar (toggle up/down) |
| GET | `/api/posts/:id/comments/` | No | Comentarios del post |
| POST | `/api/posts/:id/comments/` | Sí | Comentar |
| DELETE | `/api/posts/:pk/comments/:id/` | Sí (autor) | Borrar comentario |

### Admin (role=admin)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/admin/stats/` | Admin | Total posts, comentarios, usuarios |
| GET | `/api/admin/posts/` | Admin | Todos los posts |
| DELETE | `/api/admin/posts/:id/` | Admin | Eliminar cualquier post |
| GET | `/api/admin/comments/` | Admin | Todos los comentarios |
| DELETE | `/api/admin/comments/:id/` | Admin | Eliminar cualquier comentario |

### Docs
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/docs/` | Swagger UI interactivo |
| GET | `/api/schema/` | OpenAPI schema JSON |

---

## Variables de entorno

### Backend (`.env` en `blogreddit/`)
```env
SECRET_KEY=genera-una-clave-segura
DEBUG=False
DATABASE_URL=postgresql://user:pass@host/dbname
ALLOWED_HOSTS=tu-api.onrender.com
CORS_ALLOWED_ORIGINS=https://tu-frontend.vercel.app
```

### Frontend (`.env` en `blogreddit-frontend/`)
```env
VITE_API_URL=https://tu-api.onrender.com/api
```

---

## Instalación local

```bash
# ── Backend ──────────────────────────────────────────
cd blogreddit

# Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env (ver sección de variables)

# Migraciones
python manage.py migrate

# Superusuario
python manage.py createsuperuser

# Servidor
python manage.py runserver

# ── Frontend ─────────────────────────────────────────
cd blogreddit-frontend

npm install
npm run dev
```

---

## Deploy

| Plataforma | Servicio | Configuración |
|------------|----------|---------------|
| **Render** | Backend Django | Build: `pip install -r requirements.txt`, Start: `gunicorn config.wsgi` |
| **Vercel** | Frontend React | Auto-detect Vite, `vercel.json` para headers de seguridad |
| **Neon** | PostgreSQL 17 | Free tier, región US East (N. Virginia) |

---

## Roles de usuario

| Rol | Permisos |
|-----|---------|
| `user` | Crear posts y comentarios, votar, editar/borrar los propios |
| `moderator` | (reservado para futuro) |
| `admin` | Todo lo anterior + acceso al panel `/admin-panel` + eliminar cualquier contenido |

Para asignar rol admin via SQL:
```sql
UPDATE users_user SET role = 'admin' WHERE username = 'tu_usuario';
```

---

*EST. 2026 — ONYX BLOG — DECAY–84 EDITION*
