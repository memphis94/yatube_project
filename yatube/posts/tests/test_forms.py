from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post
from ..forms import PostForm

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='test_post',
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_create_task(self):
        """Тест на создание нового поста в БД"""
        post_count = Post.objects.count()
        form_data = {
            'text': self.post.id,
            'id_group': self.group.pk,
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.author.username}))

        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_task(self):
        """Тест на редактирование поста в БД"""
        post_count = Post.objects.count()
        self.assertEquals(
            'test_post', Post.objects.filter(pk=self.post.id)[0].text)
        form_data = {
            'text': 'test_post edit',
            'id_group': self.group.pk,
        }
        response = self.authorized_author.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}
                    ), data=form_data, follow=True
        )

        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': self.post.id}
                              )
        )

        self.assertEquals(
            'test_post edit', Post.objects.filter(pk=self.post.id)[0].text)
        self.assertEqual(Post.objects.count(), post_count)
