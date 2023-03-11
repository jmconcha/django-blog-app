from django.test import TestCase
from django.urls import reverse

from blog.models import Blog
from core.tests.utils import create_user
from blog.tests.utils import create_blog

# Create your tests here.


class CreateBlogViewTests(TestCase):
    def setUp(self):
        # create_user
        create_user(username='johndoe', password='johndoepass')
        # login user
        self.client.login(username='johndoe', password='johndoepass')

    def test_create_blog_with_unauthenticated_user(self):
        # logout user
        self.client.logout()
        response = self.client.get(reverse('blog:create_blog'))

        # going to create blog url with unauthenticated user will redirect to login page
        self.assertEqual(response.status_code, 302)
        # check if user is redirected to login page
        redirect_response = self.client.get(response.url)
        self.assertTemplateUsed('core/login.html')
        # check if message is displayed
        self.assertContains(redirect_response, 'Please login to proceed.')

    def test_create_blog_with_authenticated_user(self):
        response = self.client.get(reverse('blog:create_blog'))

        # checks if user is not redirected to login page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed('core/login.html')
        self.assertTemplateUsed('core/create_blog.html')

    def test_create_blog_with_empty_title_and_body(self):
        response = self.client.post(reverse('blog:create_blog'), {
            'status': Blog.DRAFT,
            'title': '',
            'body': '',
        })

        self.assertContains(response, 'This field is required.', count=2)

    def test_create_blog_with_active_blog(self):
        response = self.client.post(reverse('blog:create_blog'), {
            'status': Blog.ACTIVE,
            'title': 'Test Title',
            'body': 'Test Body',
        })

        # checks if user is redirected to home/front page
        self.assertEqual(response.status_code, 302)
        # redirect user
        redirect_response = self.client.get(response.url)
        self.assertTemplateUsed('core/front_page')
        self.assertContains(redirect_response, 'Test Title')
        self.assertContains(redirect_response, 'Test Body')


class SearchBlogViewTests(TestCase):
    def test_search_with_no_blogs(self):
        response = self.client.get(reverse('blog:search_blog'), {
            'query': 'Test Title',
        })

        self.assertContains(
            response, 'No blog posted yet. Be the first blogger,')

    def test_search_with_empty_query(self):
        response = self.client.get(reverse('blog:search_blog'), {
            'query': '',
        })

        self.assertContains(
            response, 'No blog posted yet. Be the first blogger,')

    def test_search_with_blogs_and_empty_query(self):
        user = create_user(username='johndoe', password='johndoepass')
        blogs = []
        for count in range(3):
            blog = create_blog(
                user, title=f'Test Title {count}', body=f'Test Body {count}', status=Blog.ACTIVE)
            blogs.append(blog)
        # sort blogs, desc by created_at
        blogs = sorted(blogs, key=lambda x: x.created_at, reverse=True)

        response = self.client.get(reverse('blog:search_blog'), {
            'query': '',
        })

        self.assertQuerysetEqual(response.context['blogs'], blogs)

    def test_search_with_draft_blogs(self):
        user = create_user(username='johndoe', password='johndoepass')
        for count in range(3):
            create_blog(
                user, title=f'Test Title {count}', body=f'Test Body {count}', status=Blog.DRAFT)

        response = self.client.get(reverse('blog:search_blog'), {
            'query': 'Test Title',
        })

        self.assertQuerysetEqual(response.context['blogs'], [])

    def test_search_with_active_blogs(self):
        user = create_user(username='johndoe', password='johndoepass')
        active_blogs = []
        for count in range(3):
            blog = create_blog(
                user, title=f'Test Title {count}', body=f'Test Body {count}', status=Blog.ACTIVE)
            active_blogs.append(blog)

        response = self.client.get(reverse('blog:search_blog'), {
            'query': 'Test Title',
        })
        # sort blogs, desc by created_at
        active_blogs = sorted(
            active_blogs, key=lambda x: x.created_at, reverse=True)

        self.assertQuerysetEqual(response.context['blogs'], active_blogs)
        # checks if active blogs are displayed
        self.assertContains(response, 'Test Title 0')
        self.assertContains(response, 'Test Body 0')
        self.assertContains(response, 'Test Body 2')
        self.assertContains(response, 'Test Title 1')
        self.assertContains(response, 'Test Body 1')
        self.assertContains(response, 'Test Title 2')

    def test_search_with_active_blogs_but_no_match(self):
        user = create_user(username='johndoe', password='johndoepass')
        active_blogs = []
        for count in range(3):
            blog = create_blog(
                user, title=f'Test Title {count}', body=f'Test Body {count}', status=Blog.ACTIVE)
            active_blogs.append(blog)

        response = self.client.get(reverse('blog:search_blog'), {
            'query': 'No Title Match',
        })
        # sort blogs, desc by created_at
        active_blogs = sorted(
            active_blogs, key=lambda x: x.created_at, reverse=True)

        # get recent blogs if no match found
        self.assertQuerysetEqual(response.context['blogs'], active_blogs)
        # then display message
        self.assertContains(
            response, "There's no blog that match your query", html=True)
        # checks if active blogs are displayed
        self.assertContains(response, 'Test Title 0')
        self.assertContains(response, 'Test Body 0')
        self.assertContains(response, 'Test Body 2')
        self.assertContains(response, 'Test Title 1')
        self.assertContains(response, 'Test Body 1')
        self.assertContains(response, 'Test Title 2')
