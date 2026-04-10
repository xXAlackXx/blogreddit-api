from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    )
    email = models.EmailField(unique=True)
    avatar = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    karma = models.IntegerField(default=0)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class ProfileTheme(models.Model):

    BANNER_PRESETS = {
        'nebula':   'linear-gradient(135deg, #1a1a2e, #16213e, #0f3460)',
        'void':     'linear-gradient(135deg, #0d1117, #161b22, #21262d)',
        'ember':    'linear-gradient(135deg, #1a0a0a, #2d1010, #3d1515)',
        'matrix':   'linear-gradient(135deg, #0a1a0a, #102d10, #153d15)',
        'solar':    'linear-gradient(135deg, #1a1a0a, #2d2d10, #3d3d15)',
        'cyber':    'linear-gradient(45deg,  #0a0a1a, #1a0a2d, #2d0a3d)',
        'deep_sea': 'linear-gradient(135deg, #0a1628, #162844, #1a3a5c)',
        'phantom':  'linear-gradient(135deg, #1a0a28, #2a1040, #3a1858)',
        'rust':     'linear-gradient(45deg,  #28100a, #402818, #584028)',
    }

    PATTERN_CHOICES = [
        ('none',  'None'),
        ('grid',  'Grid'),
        ('dots',  'Dots'),
        ('lines', 'Lines'),
        ('cross', 'Cross'),
    ]

    FONT_CHOICES = [
        ('JetBrains Mono',    'JetBrains Mono'),
        ('Space Mono',        'Space Mono'),
        ('Fira Code',         'Fira Code'),
        ('IBM Plex Mono',     'IBM Plex Mono'),
        ('Source Code Pro',   'Source Code Pro'),
        ('Inconsolata',       'Inconsolata'),
        ('Courier Prime',     'Courier Prime'),
        ('Share Tech Mono',   'Share Tech Mono'),
        ('VT323',             'VT323'),
        ('Press Start 2P',    'Press Start 2P'),
        ('Silkscreen',        'Silkscreen'),
        ('Pixelify Sans',     'Pixelify Sans'),
        ('Orbitron',          'Orbitron'),
        ('Rajdhani',          'Rajdhani'),
        ('Exo 2',             'Exo 2'),
        ('Oxanium',           'Oxanium'),
        ('Audiowide',         'Audiowide'),
        ('Chakra Petch',      'Chakra Petch'),
        ('Major Mono Display','Major Mono Display'),
    ]

    MOOD_CHOICES = [
        ('online',   '// ONLINE'),
        ('coding',   '// CODING'),
        ('afk',      '// AFK'),
        ('creating', '// CREATING'),
        ('lurking',  '// LURKING'),
        ('vibing',   '// VIBING'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile_theme',
    )
    accent_color              = models.CharField(max_length=7,  default='#A3E635')
    banner_preset             = models.CharField(max_length=20, default='nebula')
    banner_image              = models.BinaryField(null=True, blank=True)
    banner_image_content_type = models.CharField(max_length=20, null=True, blank=True)
    pattern                   = models.CharField(max_length=10, choices=PATTERN_CHOICES, default='none')
    font                      = models.CharField(max_length=30, default='JetBrains Mono')
    banner_opacity            = models.IntegerField(default=100)
    glow_intensity            = models.IntegerField(default=25)
    border_accent             = models.IntegerField(default=0)
    mood                      = models.CharField(max_length=10, choices=MOOD_CHOICES, default='online')
    created_at                = models.DateTimeField(auto_now_add=True)
    updated_at                = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profile_themes'

    def __str__(self):
        return f'Theme for {self.user.username}'

    def hex_to_rgb(self):
        h = self.accent_color.lstrip('#')
        return f'{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}'

    def get_banner_css(self):
        if self.banner_image:
            return None
        return self.BANNER_PRESETS.get(self.banner_preset, self.BANNER_PRESETS['nebula'])

    def get_pattern_css(self):
        patterns = {
            'none':  '',
            'grid':  ('repeating-linear-gradient(0deg,rgba(255,255,255,.06) 0px,'
                       'rgba(255,255,255,.06) 1px,transparent 1px,transparent 20px),'
                       'repeating-linear-gradient(90deg,rgba(255,255,255,.06) 0px,'
                       'rgba(255,255,255,.06) 1px,transparent 1px,transparent 20px)'),
            'dots':  'radial-gradient(circle,rgba(255,255,255,.08) 1px,transparent 1px)',
            'lines': ('repeating-linear-gradient(45deg,rgba(255,255,255,.04) 0px,'
                       'rgba(255,255,255,.04) 1px,transparent 1px,transparent 8px)'),
            'cross': ('repeating-linear-gradient(45deg,rgba(255,255,255,.04) 0px,'
                       'rgba(255,255,255,.04) 1px,transparent 1px,transparent 12px),'
                       'repeating-linear-gradient(-45deg,rgba(255,255,255,.04) 0px,'
                       'rgba(255,255,255,.04) 1px,transparent 1px,transparent 12px)'),
        }
        return patterns.get(self.pattern, '')

    def get_mood_display(self):
        return dict(self.MOOD_CHOICES).get(self.mood, '// ONLINE')

    def get_css_vars(self):
        rgb = self.hex_to_rgb()
        gi  = self.glow_intensity
        bi  = self.border_accent
        return {
            '--user-accent':        self.accent_color,
            '--user-accent-rgb':    rgb,
            '--user-accent-glow':   f'0 0 {gi*0.35:.1f}px rgba({rgb},{gi*0.004:.3f})',
            '--user-accent-bg':     f'rgba({rgb},0.12)',
            '--user-banner-opacity':str(self.banner_opacity / 100),
            '--user-border-accent': f'rgba({rgb},{bi/100:.2f})' if bi > 0 else '',
            '--user-font':          f"'{self.font}', monospace",
        }