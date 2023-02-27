from django.test import TestCase
from django.urls import reverse

from core.tests.utils import create_user
from blog.models import Blog

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
        self.assertContains(redirect_response, 'You need to login.')
    
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