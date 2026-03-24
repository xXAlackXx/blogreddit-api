from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import F
from django.db import transaction
from .models import Post, Comment, Vote
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['author']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'upvotes', 'downvotes']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_pk']).order_by('-created_at')

    def perform_create(self, serializer):
        post = Post.objects.get(pk=self.kwargs['post_pk'])
        serializer.save(author=self.request.user, post=post)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_pk'])

class VoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        vote_type = request.data.get('vote_type')
        if vote_type not in ['upvote', 'downvote']:
            return Response({'error': 'vote_type must be upvote or downvote'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            existing_vote = Vote.objects.select_for_update().filter(user=request.user, post=post).first()

            if existing_vote:
                if existing_vote.vote_type == vote_type:
                    # mismo voto -> cancelar
                    if vote_type == 'upvote':
                        Post.objects.filter(pk=pk).update(upvotes=F('upvotes') - 1)
                    else:
                        Post.objects.filter(pk=pk).update(downvotes=F('downvotes') - 1)
                    existing_vote.delete()
                    return Response({'message': 'Voto eliminado'}, status=status.HTTP_200_OK)
                else:
                    # voto diferente -> cambiar
                    if vote_type == 'upvote':
                        Post.objects.filter(pk=pk).update(upvotes=F('upvotes') + 1, downvotes=F('downvotes') - 1)
                    else:
                        Post.objects.filter(pk=pk).update(downvotes=F('downvotes') + 1, upvotes=F('upvotes') - 1)
                    existing_vote.vote_type = vote_type
                    existing_vote.save()
                    return Response({'message': 'Voto actualizado'}, status=status.HTTP_200_OK)
            else:
                # voto nuevo
                Vote.objects.create(user=request.user, post=post, vote_type=vote_type)
                if vote_type == 'upvote':
                    Post.objects.filter(pk=pk).update(upvotes=F('upvotes') + 1)
                else:
                    Post.objects.filter(pk=pk).update(downvotes=F('downvotes') + 1)
                return Response({'message': 'Voto registrado'}, status=status.HTTP_201_CREATED)