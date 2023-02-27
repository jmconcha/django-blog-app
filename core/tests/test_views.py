from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.urls import reverse

from blog.models import Blog
from .utils import create_user
from blog.tests.utils import create_blog

# Create your tests here.


class FrontPageViewTests(TestCase):
    def test_front_page_with_no_blogs(self):
        response = self.client.get(reverse('core:front_page'))
        
        self.assertTemplateUsed(response, 'core/front_page.html')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['blogs'], [])
        self.assertContains(response, 'No blog posted yet. Be the first blogger,')
        self.assertContains(response, 'create blog now!')
        
    def test_front_page_with_draft_blogs(self):
        user = create_user(username='johndoe', password='johndoepass')
    
        for count in range(3):
            create_blog(user, title=f'Test Title {count}', body=f'Test Body {count}')
            
        response = self.client.get(reverse('core:front_page'))
        
        self.assertTemplateUsed(response, 'core/front_page.html')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['blogs'], [])
        self.assertContains(response, 'No blog posted yet. Be the first blogger,')
        self.assertContains(response, 'create blog now!')
        
    def test_front_page_with_active_blogs(self):
        user = create_user(username='johndoe', password='johndoepass')
        blogs = []
        
        for count in range(3):
            blog = create_blog(user, title=f'Blog Title {count}', body=f'This is blog body {count}', status=Blog.ACTIVE)
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
        
        
class RegisterUserViewTests(TestCase):
    def test_register_with_empty_inputs(self):
        response = self.client.post(reverse('core:register'), {
            'username': '',
            'email': '',
            'password': '',
            'confirm-password': '',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['errors'], {
            'username': 'Username is required',
            'password': 'Password is required',
            'confirm_password': 'Confirm password is required',
        })
        self.assertContains(response, 'Username is required')
        self.assertContains(response, 'Password is required')
        self.assertContains(response, 'Confirm password is required')
        
    def test_register_with_mismatch_password(self):
        response = self.client.post(reverse('core:register'), {
            'username': 'testuser',
            'password': 'pass123',
            'confirm-password': '123pass',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['errors'], {
            'password': 'Password must match',
            'confirm_password': 'Password must match',
        })
        self.assertContains(response, 'Password must match', count=2)
        
    def test_register_with_correct_inputs(self):
        response = self.client.post(reverse('core:register'), {
            'username': 'testuser',
            'email': 'testuser@gmail.com',
            'password': 'pass123',
            'confirm-password': 'pass123',
        })
        self.assertEqual(response.status_code, 302)
        
        # checks if user is created
        user = User.objects.filter(username='testuser').first()
        self.assertNotEqual(user, None)
        
        # after redirection
        redirect_response = self.client.get(reverse('core:front_page'))
        self.assertContains(redirect_response, 'You are now successfully registered')
        
        
class LoginUserViewTests(TestCase):
    def test_login_with_empty_inputs(self):
        response = self.client.post(reverse('core:login'), {
            'username': '',
            'password': '',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['errors'], {
            'username': 'Username is required',
            'password': 'Password is required',
        })
        self.assertContains(response, 'Username is required')
        self.assertContains(response, 'Password is required')
        
    def test_login_with_unregistered_user(self):
        response = self.client.post(reverse('core:login'), {
            'username': 'unregistereduser',
            'password': 'unregisteredpass',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your username and password didn't match. Please try again.", html=True)
        
    def test_login_with_registered_user(self):
        # register user
        User.objects.create_user(username='testuser', password='testuserpass')
        
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': 'testuserpass',
        })
        self.assertEqual(response.status_code, 302)
        
        redirect_response = self.client.get(reverse('core:front_page'))
        self.assertContains(redirect_response, text='Logout', html=True)
        
        
class LogoutUserViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_logout_view(self):
        User.objects.create_user(username='testuser', password='testpass123')
        
        # login user
        is_logged_in = self.client.login(username='testuser', password='testpass123')
        self.assertEqual(is_logged_in, True)
        after_login_response = self.client.get(reverse('core:front_page'))
        self.assertContains(after_login_response, 'Logout')

        # logout user        
        self.client.logout()
        after_logout_response = self.client.get(reverse('core:front_page'))
        self.assertContains(after_logout_response, 'Login')