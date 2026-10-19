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
