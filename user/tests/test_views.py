from django.test import TestCase
from django.urls import reverse

from core.tests.utils import create_user
from blog.tests.utils import create_blog
from blog.models import Blog

# Create your tests here.
class UserBlogsViewWithVisitorTests(TestCase):
    def setUp(self):
        self.author = create_user(username='johndoe', password='johndoepass')
        self.visitor = create_user(username='tom', password='tompass')
        self.client.login(username='tom', password='tompass')
    
    def test_user_blogs_with_author_do_not_exist(self):
        response = self.client.get(reverse('user:user_blogs', args=('janedoe',)))
        
        # if author don't exist redirect user to home page
        self.assertEqual(response.status_code, 302)
        redirect_response = self.client.get(response.url)
        self.assertEqual(redirect_response.status_code, 200)
        # checks message display
        self.assertContains(redirect_response, "Blogger don't exist", html=True)
    
    def test_user_blogs_with_no_blogs(self):
        response = self.client.get(reverse('user:user_blogs', args=('johndoe',)))
        
        # checks author with no blogs
        self.assertQuerysetEqual(response.context['blogs'], [])
        self.assertContains(response, f'No active blogs for johndoe')
    
    def test_user_blogs_with_draft_blogs(self):
        for count in range(3):
            create_blog(self.author, title=f'Test Title {count}', body=f'Test Body {count}', status=Blog.DRAFT)
            
        response = self.client.get(reverse('user:user_blogs', args=('johndoe',)))
        self.assertQuerysetEqual(response.context['blogs'], [])
        self.assertContains(response, f'No active blogs for johndoe')
        
    def test_user_with_active_blogs(self):
        active_blogs = []
        for count in range(3):
            blog = create_blog(self.author, title=f'Test Title {count}', body=f'Test Body {count}', status=Blog.ACTIVE)
            active_blogs.append(blog)
        # sort blog by created_at, descending
        active_blogs = sorted(active_blogs, key=lambda b: b.id, reverse=True)
            
        response = self.client.get(reverse('user:user_blogs', args=('johndoe',)))
        self.assertQuerysetEqual(response.context['blogs'], active_blogs)
        self.assertNotContains(response, f'No active blogs for johndoe') 
        
        
class UserBlogsViewWithAuthorTests(TestCase):
    def setUp(self):
        self.author = create_user(username='johndoe', password='johndoepass')
        self.client.login(username='johndoe', password='johndoepass')
        
    def test_author_without_blogs(self):
        response = self.client.get(reverse('user:user_blogs', args=('johndoe',)))
        
        self.assertQuerysetEqual(response.context['blogs'], [])
        self.assertContains(response, 'You have no blog yet. Create your first blog')
        
    def test_author_with_draft_and_active_blogs(self):
        draft_blog = create_blog(self.author, title='This is Draft Blog', body='Draft Blog Body', status=Blog.DRAFT)
        active_blog = create_blog(self.author, title='This is Active Blog', body='Active Blog Body', status=Blog.ACTIVE)
        
        response = self.client.get(reverse('user:user_blogs', args=('johndoe',)))
        
        self.assertQuerysetEqual(response.context['blogs'], [active_blog, draft_blog])
        self.assertContains(response, 'This is Draft Blog')
        self.assertContains(response, 'Draft Blog Body')
        # DRAFT identifier
        self.assertContains(response, 'DRAFT')
        self.assertContains(response, 'This is Active Blog')
        self.assertContains(response, 'Active Blog Body')