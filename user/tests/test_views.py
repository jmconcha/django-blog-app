from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from core.tests.utils import create_user
from blog.tests.utils import create_blog
from blog.models import Blog
from user.models import UserProfile

# Create your tests here.


class UserBlogsViewWithVisitorTests(TestCase):
    def setUp(self):
        self.author = create_user(username='johndoe', password='johndoepass')
        self.visitor = create_user(username='tom', password='tompass')
        self.client.login(username='tom', password='tompass')

    def test_user_blogs_with_author_do_not_exist(self):
        response = self.client.get(
            reverse('user:user_blogs', args=('janedoe',)))

        # if author don't exist redirect user to home page
        self.assertEqual(response.status_code, 302)
        redirect_response = self.client.get(response.url)
        self.assertEqual(redirect_response.status_code, 200)
        # checks message display
        self.assertContains(redirect_response,
                            "Blogger don't exist", html=True)

    def test_user_blogs_with_no_blogs(self):
        response = self.client.get(
            reverse('user:user_blogs', args=('johndoe',)))

        # checks author with no blogs
        self.assertQuerysetEqual(response.context['blogs'], [])
        self.assertContains(response, 'No active blogs for johndoe')

    def test_user_blogs_with_draft_blogs(self):
        for count in range(3):
            create_blog(
                self.author, title=f'Test Title {count}', body=f'Test Body {count}', status=Blog.DRAFT)

        response = self.client.get(
            reverse('user:user_blogs', args=('johndoe',)))
        self.assertQuerysetEqual(response.context['blogs'], [])
        self.assertContains(response, 'No active blogs for johndoe')

    def test_user_with_active_blogs(self):
        active_blogs = []
        for count in range(3):
            blog = create_blog(
                self.author, title=f'Test Title {count}', body=f'Test Body {count}', status=Blog.ACTIVE)
            active_blogs.append(blog)
        # sort blog by created_at, descending
        active_blogs = sorted(active_blogs, key=lambda b: b.id, reverse=True)

        response = self.client.get(
            reverse('user:user_blogs', args=('johndoe',)))
        self.assertQuerysetEqual(response.context['blogs'], active_blogs)
        self.assertNotContains(response, 'No active blogs for johndoe')


class UserBlogsViewWithAuthorTests(TestCase):
    def setUp(self):
        self.author = create_user(username='johndoe', password='johndoepass')
        self.client.login(username='johndoe', password='johndoepass')

    def test_author_without_blogs(self):
        response = self.client.get(
            reverse('user:user_blogs', args=('johndoe',)))

        self.assertQuerysetEqual(response.context['blogs'], [])
        self.assertContains(
            response, 'You have no blog yet. Create your first blog')

    def test_author_with_draft_and_active_blogs(self):
        draft_blog = create_blog(
            self.author, title='This is Draft Blog', body='Draft Blog Body', status=Blog.DRAFT)
        active_blog = create_blog(
            self.author, title='This is Active Blog', body='Active Blog Body', status=Blog.ACTIVE)

        response = self.client.get(
            reverse('user:user_blogs', args=('johndoe',)))

        self.assertQuerysetEqual(response.context['blogs'], [
                                 active_blog, draft_blog])
        self.assertContains(response, 'This is Draft Blog')
        self.assertContains(response, 'Draft Blog Body')
        # DRAFT identifier
        self.assertContains(response, 'DRAFT')
        self.assertContains(response, 'This is Active Blog')
        self.assertContains(response, 'Active Blog Body')


class UserProfileViewTests(TestCase):
    def setUp(self):
        create_user(username='john', password='johnpass')
        user = create_user(username='jane', password='janepass')
        user.first_name = 'Jane'
        user.last_name = 'Doe'
        user.save()

        user_profile = UserProfile(user=user, bio='This is Jane Doe Bio',
                                   location='Philippines', birth_date=timezone.datetime(1990, 12, 27).date())
        user_profile.save()

        self.user = user
        self.client.login(username='jane', password='janepass')

    def test_profile_with_unauthenticated_user(self):
        self.client.logout()

        response = self.client.get(
            reverse('user:profile', args=('jane',)))
        self.assertEqual(response.status_code, 302)

        redirect_response = self.client.get(response.url)
        self.assertContains(redirect_response, 'Please login to proceed.')

    def test_profile_with_unauthorized_user(self):
        # jane is logged in user who visits john profile
        response = self.client.get(
            reverse('user:profile', args=('john',)))

        self.assertContains(response, '403 Forbidden', status_code=403)

    def test_profile_with_user_that_has_profile_data(self):
        user = self.user
        user_profile = user.rel_profile
        user_info = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': user_profile.bio,
            'location': user_profile.location,
            'birth_date': user_profile.birth_date,
            'profile_picture': '/media/thumbnails/default.png',
        }

        response = self.client.get(
            reverse('user:profile', args=('jane',)))

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.context['user_info'], user_info)

    def test_update_profile_with_user_inputs(self):
        data = {
            'first_name': 'Jane Updated',
            'last_name': 'Doe Updated',
            'bio': 'This is Jane Update Bio',
            'location': 'Philippines Updated',
            'birth_date': '01/28/1991',
        }
        user_info = {
            'username': self.user.username,
            'first_name': 'Jane Updated',
            'last_name': 'Doe Updated',
            'bio': 'This is Jane Update Bio',
            'location': 'Philippines Updated',
            'birth_date': timezone.datetime(1991, 1, 28).date(),
            'profile_picture': '/media/thumbnails/default.png',
        }

        response = self.client.post(
            reverse('user:profile', args=('jane',)), data)
        self.assertEqual(response.status_code, 302)

        # checks if user profile in database has been updated
        jane = User.objects.get(username='jane')
        jane_profile = jane.rel_profile
        self.assertEqual(jane.first_name, 'Jane Updated')
        self.assertEqual(jane.last_name, 'Doe Updated')
        self.assertEqual(jane_profile.bio, 'This is Jane Update Bio')
        self.assertEqual(jane_profile.location, 'Philippines Updated')
        self.assertEqual(jane_profile.birth_date,
                         timezone.datetime(1991, 1, 28).date())

        redirect_response = self.client.get(response.url)
        self.assertEqual(redirect_response.status_code, 200)

        # checks if values are passed to UI through context
        self.assertDictEqual(redirect_response.context['user_info'], user_info)

        # checks if values are in UI
        self.assertContains(redirect_response, 'Jane Updated')
        self.assertContains(redirect_response, 'Doe Updated')
        self.assertContains(redirect_response, 'This is Jane Update Bio')
        self.assertContains(redirect_response, 'Philippines Updated')
        # does not include this assertion because the date in UI are results of JavaScript
        # self.assertContains(redirect_response, '01/28/1991')

    def test_update_profile_with_empty_inputs(self):
        data = {
            'first_name': '',
            'last_name': '',
            'bio': '',
            'location': '',
            'birth_date': '',
        }
        user_info = {
            'username': self.user.username,
            'first_name': '',
            'last_name': '',
            'bio': '',
            'location': '',
            'birth_date': None,
            'profile_picture': '/media/thumbnails/default.png',
        }

        response = self.client.post(
            reverse('user:profile', args=('jane',)), data)
        self.assertEqual(response.status_code, 302)

        redirect_response = self.client.get(response.url)
        self.assertEqual(redirect_response.status_code, 200)

        self.assertDictEqual(redirect_response.context['user_info'], user_info)

    def test_redirect_after_success_profile_update(self):
        data = {
            'first_name': 'Jane Updated',
            'last_name': 'Doe Updated',
            'bio': 'This is Jane Update Bio',
            'location': 'Philippines Updated',
            'birth_date': '01/28/1991',
        }

        response = self.client.post(
            reverse('user:profile', args=('jane',)), data)
        redirect_response = self.client.get(response.url)

        self.assertContains(redirect_response,
                            'You successfully updated your profile.')
        self.assertRedirects(response, reverse(
            'user:profile', args=('jane', )), 302, 200)

    def test_profile_with_new_user(self):
        self.client.logout()
        self.client.post(reverse('core:register'), {
            'username': 'newuser',
            'password': 'newuserpass',
            'confirm_password': 'newuserpass'
        })
        response = self.client.get(reverse('user:profile', args=('newuser',)))

        self.assertEqual(response.status_code, 200)
