import urllib.parse
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


class UpdateBlogViewTests(TestCase):
    def setUp(self):
        self.user = create_user(username='jane', password='janepass')
        self.blog = create_blog(
            user=self.user, title='Draft Blog Title', body='Draft Blog Body')
        self.client.login(username='jane', password='janepass')

    def test_update_blog_with_non_existing_blog(self):
        get_response = self.client.get(
            reverse('blog:update_blog', args=('non-existing-blog-slug',)))
        self.assertEqual(get_response.status_code, 404)
        self.assertContains(get_response,
                            'Not Found', status_code=404)

        post_response = self.client.post(
            reverse('blog:update_blog', args=('non-existing-blog-slug',)))
        self.assertEqual(post_response.status_code, 404)
        self.assertContains(post_response,
                            'Not Found', status_code=404)

    def test_update_blog_with_unathenticated_user(self):
        self.client.logout()

        update_blog_url = reverse('blog:update_blog', args=(self.blog.slug,))
        response = self.client.get(update_blog_url)

        login_url = reverse('core:login')
        next_url = urllib.parse.quote(update_blog_url, safe='')
        redirect_url = f'{login_url}?next={next_url}'
        self.assertRedirects(response, redirect_url, 302, 200)

    def test_update_blog_with_unauthorized_user(self):
        create_user(username='john', password='johnpass')
        self.client.logout()
        self.client.login(username='john', password='johnpass')

        # *TODO: checks if user is receive a 403 forbidden response
        response = self.client.get(
            reverse('blog:update_blog', args=(self.blog.slug,)))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, '403 Forbidden', status_code=403)

    def test_update_blog_without_title_and_body(self):
        data = {
            'status': Blog.DRAFT,
            'title': '',
            'body': '',
        }
        response = self.client.post(
            reverse('blog:update_blog', args=(self.blog.slug,)), data)

        # *TODO: checks if errors displayed on form
        self.assertContains(response, 'This field is required.', count=2)

    def test_update_blog_with_title_and_body(self):
        data = {
            'status': Blog.DRAFT,
            'title': 'Draft Blog Title Updated',
            'body': 'Draft Blog Body Updated',
        }
        response = self.client.post(
            reverse('blog:update_blog', args=(self.blog.slug,)), data)
        redirect_response = self.client.get(response.url)

        # get updated blog
        updated_blog = Blog.objects.get(pk=self.blog.id)

        self.assertContains(
            redirect_response, 'Your blog has been updated.')
        self.assertRedirects(response, reverse(
            'blog:blog_detail', args=(updated_blog.slug,)), 302, 200)
        self.assertEqual(updated_blog.title, 'Draft Blog Title Updated')
        self.assertEqual(updated_blog.body, 'Draft Blog Body Updated')

    def test_update_blog_with_active_blog(self):
        active_blog = create_blog(
            self.user, title='Active Blog Title', body='Active Blog Title Body', status=Blog.ACTIVE)
        # *TODO: checks if user is redirected to view/detail blog page
        response = self.client.post(
            reverse('blog:update_blog', args=(active_blog.slug,)))

        self.assertRedirects(response, reverse(
            'blog:blog_detail', args=(active_blog.slug,)), 302, 200)
