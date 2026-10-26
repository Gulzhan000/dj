from django.test import Client, TestCase
from django.urls import reverse

from .models import Blog


class BlogListDetailTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.blog = Blog.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание статьи',
            author='Тестовый автор',
        )

    def test_new_blog_likes_default_to_zero(self):
        self.assertEqual(self.blog.likes, 0)

    def test_blog_string_representation(self):
        self.assertEqual(str(self.blog), 'Тестовый заголовок')

    def test_list_page_returns_200(self):
        response = self.client.get(reverse('blog:list'))
        self.assertEqual(response.status_code, 200)

    def test_list_page_uses_expected_template(self):
        response = self.client.get(reverse('blog:list'))
        self.assertTemplateUsed(response, 'blog/blog_list.html')

    def test_list_page_contains_blog_data(self):
        response = self.client.get(reverse('blog:list'))
        self.assertContains(response, self.blog.title)
        self.assertContains(response, self.blog.author)

    def test_list_context_contains_created_blog_and_id(self):
        response = self.client.get(reverse('blog:list'))
        blogs = list(response.context['blogs'])
        self.assertIn(self.blog, blogs)
        self.assertEqual(blogs[0].id, self.blog.id)

    def test_list_page_link_opens_detail_page(self):
        detail_url = reverse('blog:detail', args=[self.blog.id])
        list_response = self.client.get(reverse('blog:list'))
        self.assertContains(list_response, f'href="{detail_url}"')
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)

    def test_detail_page_uses_expected_template_and_content(self):
        response = self.client.get(reverse('blog:detail', args=[self.blog.id]))
        self.assertTemplateUsed(response, 'blog/blog_detail.html')
        self.assertContains(response, self.blog.title)
        self.assertContains(response, self.blog.description)
        self.assertEqual(response.context['blog'].id, self.blog.id)

    def test_detail_page_returns_404_for_missing_id(self):
        response = self.client.get(reverse('blog:detail', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_detail_get_increments_likes_by_one(self):
        self.client.get(reverse('blog:detail', args=[self.blog.id]))
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.likes, 1)

    def test_each_detail_get_increments_likes(self):
        url = reverse('blog:detail', args=[self.blog.id])
        self.client.get(url)
        self.client.get(url)
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.likes, 2)


class BlogCRUDTests(TestCase):
    def setUp(self):
        self.blog = Blog.objects.create(title='Исходная статья', description='Описание', author='Автор', likes=5)
        self.data = {'title': 'Новая статья', 'description': 'Текст статьи', 'author': 'Гульжан'}

    def test_create_get_shows_empty_form(self):
        response = self.client.get(reverse('blog:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_form.html')
        self.assertFalse(response.context['form'].is_bound)

    def test_create_post_saves_and_redirects(self):
        response = self.client.post(reverse('blog:create'), self.data)
        self.assertRedirects(response, reverse('blog:list'))
        created = Blog.objects.get(title=self.data['title'])
        self.assertEqual(created.description, self.data['description'])
        self.assertEqual(created.author, self.data['author'])
        self.assertEqual(created.likes, 0)

    def test_create_rejects_each_blank_field(self):
        for field in self.data:
            with self.subTest(field=field):
                response = self.client.post(reverse('blog:create'), {**self.data, field: '   '})
                self.assertFormError(response.context['form'], field, 'Обязательное поле.')
                self.assertEqual(Blog.objects.count(), 1)

    def test_create_rejects_long_title(self):
        response = self.client.post(reverse('blog:create'), {**self.data, 'title': 'x' * 201})
        self.assertIn('title', response.context['form'].errors)
        self.assertEqual(Blog.objects.count(), 1)

    def test_create_rejects_long_author(self):
        response = self.client.post(reverse('blog:create'), {**self.data, 'author': 'x' * 121})
        self.assertIn('author', response.context['form'].errors)
        self.assertEqual(Blog.objects.count(), 1)

    def test_update_get_prefills_form(self):
        response = self.client.get(reverse('blog:update', args=[self.blog.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_form.html')
        self.assertEqual(response.context['form'].instance, self.blog)
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.likes, 5)

    def test_update_post_changes_existing_record(self):
        response = self.client.post(reverse('blog:update', args=[self.blog.pk]), self.data)
        self.assertRedirects(response, reverse('blog:list'))
        self.blog.refresh_from_db()
        self.assertEqual((self.blog.title, self.blog.description, self.blog.author), tuple(self.data.values()))
        self.assertEqual(self.blog.likes, 5)
        self.assertEqual(Blog.objects.count(), 1)

    def test_invalid_update_preserves_record(self):
        response = self.client.post(reverse('blog:update', args=[self.blog.pk]), {**self.data, 'title': ''})
        self.assertTrue(response.context['form'].errors)
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.title, 'Исходная статья')

    def test_delete_get_only_asks_for_confirmation(self):
        response = self.client.get(reverse('blog:delete', args=[self.blog.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_confirm_delete.html')
        self.assertContains(response, self.blog.title)
        self.assertTrue(Blog.objects.filter(pk=self.blog.pk).exists())

    def test_delete_post_removes_only_target(self):
        other = Blog.objects.create(**self.data)
        response = self.client.post(reverse('blog:delete', args=[self.blog.pk]))
        self.assertRedirects(response, reverse('blog:list'))
        self.assertFalse(Blog.objects.filter(pk=self.blog.pk).exists())
        self.assertTrue(Blog.objects.filter(pk=other.pk).exists())

    def test_missing_update_and_delete_return_404(self):
        for name in ['update', 'delete']:
            for method in ['get', 'post']:
                with self.subTest(name=name, method=method):
                    response = getattr(self.client, method)(reverse('blog:' + name, args=[99999]))
                    self.assertEqual(response.status_code, 404)

    def test_mutations_reject_unsupported_methods(self):
        for name in ['create', 'update', 'delete']:
            url = reverse('blog:' + name, args=[] if name == 'create' else [self.blog.pk])
            with self.subTest(name=name):
                self.assertEqual(self.client.put(url).status_code, 405)
        self.assertEqual(Blog.objects.count(), 1)

    def test_csrf_is_required_for_all_mutations(self):
        client = Client(enforce_csrf_checks=True)
        for name in ['create', 'update', 'delete']:
            url = reverse('blog:' + name, args=[] if name == 'create' else [self.blog.pk])
            with self.subTest(name=name):
                self.assertEqual(client.post(url, self.data).status_code, 403)
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.title, 'Исходная статья')
        self.assertEqual(Blog.objects.count(), 1)

    def test_valid_csrf_token_allows_create(self):
        client = Client(enforce_csrf_checks=True)
        client.get(reverse('blog:create'))
        token = client.cookies['csrftoken'].value
        response = client.post(reverse('blog:create'), {**self.data, 'csrfmiddlewaretoken': token})
        self.assertRedirects(response, reverse('blog:list'))
        self.assertEqual(Blog.objects.count(), 2)

    def test_empty_list_message(self):
        Blog.objects.all().delete()
        self.assertContains(self.client.get(reverse('blog:list')), 'Статей пока нет.')

    def test_list_contains_crud_links(self):
        response = self.client.get(reverse('blog:list'))
        self.assertContains(response, reverse('blog:create'))
        for name in ['update', 'delete']:
            self.assertContains(response, reverse('blog:' + name, args=[self.blog.pk]))

    def test_html_in_title_is_escaped(self):
        self.blog.title = '<script>alert(1)</script>'
        self.blog.save()
        response = self.client.get(reverse('blog:list'))
        self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertNotContains(response, self.blog.title)

    def test_form_excludes_counter(self):
        from .forms import BlogForm
        self.assertEqual(list(BlogForm().fields), ['title', 'description', 'author'])

    def test_post_cannot_override_counter(self):
        self.client.post(reverse('blog:create'), {**self.data, 'likes': 999})
        self.assertEqual(Blog.objects.get(title=self.data['title']).likes, 0)
