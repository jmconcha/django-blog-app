from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.urls import reverse

from blog.models import Blog
from blog.utils import title_as_slug
from . import views

# Create your tests here.

def create_user(username='johndoe', password='johndoe', email='johndoe@gmail.com', first_name='john', last_name='doe'):
    return User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)

def create_blog(user, status=Blog.DRAFT, title=f'Blog Title', body=f'This is the blog body.'):
    return Blog.objects.create(author=user, slug=title_as_slug(title), status=status, title=title, body=body)

class FrontPageViewTests(TestCase):
    def test_front_page_with_no_blogs(self):
        response = self.client.get(reverse('core:front_page'))
        
        self.assertTemplateUsed(response, 'core/front_page.html')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['blogs'], [])
        self.assertContains(response, 'No blog posted yet. Be the first blogger,')
        self.assertContains(response, 'create blog now!')
        
    def test_front_page_with_draft_blogs(self):
        user = create_user()
    
        for _ in range(3):
            create_blog(user)
            
        response = self.client.get(reverse('core:front_page'))
        
        self.assertTemplateUsed(response, 'core/front_page.html')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['blogs'], [])
        self.assertContains(response, 'No blog posted yet. Be the first blogger,')
        self.assertContains(response, 'create blog now!')
        
    def test_front_page_with_active_blogs(self):
        user = create_user()
        blogs = []
        
        for count in range(3):
            blog = create_blog(user, Blog.ACTIVE, f'Blog Title {count}', f'This is blog body {count}')
            blogs.append(blog)
            
        response = self.client.get(reverse('core:front_page'))
        # sort blog by created_at, descending
        blogs = sorted(blogs, key=lambda b: b.id, reverse=True)
        
        self.assertTemplateUsed(response, 'core/front_page.html')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['blogs'], blogs)
        self.assertNotContains(response, 'No blog posted yet. Be the first blogger,')
        self.assertNotContains(response, 'create blog now!')


class NavbarTemplateTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='jane', password='jane')
        self.user = user
        self.client.login(username='jane', password='jane')
    
    def test_navbar_with_unauthenticated_user(self):
        # logout user
        self.client.logout()
        response = self.client.get(reverse('core:front_page'))
        
        self.assertTemplateUsed(response, 'core/navbar.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Sign up')
        self.assertNotContains(response, 'Logout')
        
        
    def test_navbar_with_authenticated_user(self):
        response = self.client.get(reverse('core:front_page'))

        self.assertEqual(self.user.is_authenticated, True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/navbar.html')
        self.assertNotContains(response, 'Login')
        self.assertNotContains(response, 'Sign up')
        self.assertContains(response, 'Logout')