from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Post

User = get_user_model()

class PostTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.post = Post.objects.create(
            title='Test post',
            content='Test content',
            author=self.user
        )

    def test_list_posts(self):
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post(self):
        data = {'title': 'Nuevo post', 'content': 'Contenido'}
        response = self.client.post('/api/posts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_post_unauthenticated(self):
        self.client.logout()
        data = {'title': 'Nuevo post', 'content': 'Contenido'}
        response = self.client.post('/api/posts/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_vote_post(self):
        response = self.client.post(f'/api/posts/{self.post.id}/vote/', {'vote_type': 'upvote'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_search_posts(self):
        response = self.client.get('/api/posts/?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)