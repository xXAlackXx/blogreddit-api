import os
import uuid
import cloudinary
import cloudinary.uploader
from django.core.files.storage import Storage


class CloudinaryStorage(Storage):
    """
    Custom storage backend using cloudinary SDK directly.
    Compatible with Django 6+ (no dependency on django-cloudinary-storage).
    Stores the full Cloudinary HTTPS URL as the file name in the DB.
    """

    def __init__(self):
        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
            api_key=os.environ.get('CLOUDINARY_API_KEY', ''),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET', ''),
            secure=True,
        )

    def _save(self, name, content):
        result = cloudinary.uploader.upload(
            content,
            public_id=f"media/{uuid.uuid4().hex}",
            overwrite=True,
            resource_type='image',
        )
        return result['secure_url']

    def url(self, name):
        # name is already the full Cloudinary HTTPS URL stored in DB
        return name

    def exists(self, name):
        return False

    def get_available_name(self, name, max_length=None):
        return name

    def _open(self, name, mode='rb'):
        raise NotImplementedError("Use the URL directly to access Cloudinary files.")

    def delete(self, name):
        pass

    def size(self, name):
        return 0
