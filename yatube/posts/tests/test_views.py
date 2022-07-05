from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()

class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='test_description',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='test_description_2',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='test_post',
        )
    
    def setUp(self):        
        self.guest_client = Client()        
        self.user = User.objects.create_user(username='user')        
        self.authorized_client = Client()        
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()        
        self.authorized_author.force_login(self.author)

   
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""        
        templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/create_post.html': reverse('posts:post_edit', kwargs={
                'post_id': self.post.id}),          
            'posts/post_detail.html': reverse('posts:post_detail', kwargs={
                'post_id': self.post.id}),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': self.author.username})
            ),
        }       
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        context = response.context['page_obj'][0]
        index_text_0 = context.text
        index_author_0 = context.author
        index_group_0 = context.group
        self.assertEqual(index_text_0, self.post.text)
        self.assertEqual(index_author_0, self.author)
        self.assertEqual(index_group_0, self.group)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:group_list', kwargs={
            'slug': self.group.slug}))
        context = response.context['page_obj'][0]
        post_text_0 = context.text
        post_group_0 = context.group
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse('posts:profile', kwargs={
            'username': self.author.username}))
        context = response.context['page_obj'][0]
        post_text_0 = context.text
        post_author_0 = context.author
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.author)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id}))
        self.assertEqual(
            response.context['post'].text, self.post.text)

    def test_edit_post_show_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)                
                self.assertIsInstance(form_field, expected)

    def test_check_post_on_create(self):
        """Проверка, что пост добавляется в index, group_list
         и profile при указании группы.
         """
        pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.author}),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_author.get(page)
                self.assertEqual(response.context.get('page_obj')[0],
                                 self.post, f'{self.post.id}')

    def test_post_in_group(self):
        """Проверка, что пост не находится в другой группе."""
        response = self.authorized_author.get(
            reverse('posts:group_list', kwargs={'slug': self.group_2.slug}))        
        self.assertEqual(len(response.context['page_obj']), 0)

class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовая группа 3',
            slug='test-slug_3',
            description='test_description_3',
        )

        for i in range(0, 13):
            Post.objects.create(
                text=f'test_post_{i}',
                author=cls.author,
                group=cls.group,
            )
    
    def test_first_page_contains_ten_records(self):
        """Первая страница index содержит десять записей."""
        response = self.authorized_author.get(reverse('posts:index'))
        self.assertEquals(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Вторая страница index содердит три записи."""
        response = self.authorized_author.get(reverse('posts:index') + '?page=2')
        self.assertEquals(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        """Первая страница group_list содержит десять записей.."""
        response = self.authorized_author.get(reverse('posts:group_list', kwargs={
            'slug': self.group.slug}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_three_records(self):
        """Вторая страница group_list содердит три записи."""
        response = self.authorized_author.get(reverse('posts:group_list', kwargs={
        'slug': self.group.slug}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        """Первая страница profile содержит десять записей."""
        response = self.authorized_author.get(reverse('posts:profile', kwargs={
            'username': self.author.username}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        """Вторая страница profile содердит три записи."""
        response = self.authorized_author.get(reverse('posts:profile', kwargs={
            'username': self.author.username}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)