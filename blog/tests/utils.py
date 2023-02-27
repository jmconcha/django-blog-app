from blog.utils import title_as_slug
from blog.models import Blog

def create_blog(user, title, body, status=Blog.DRAFT):
    return Blog.objects.create(author=user, slug=title_as_slug(title), status=status, title=title, body=body)