
# Easygen

Easygen is a static site generator for django. It has no dependencies and has a pretty straightforward configuration.

Easygen follows a pattern similar to [django's sitemap framework](https://docs.djangoproject.com/en/dev/ref/contrib/sitemaps/). You configure easygen with a series of collections (that define pages to generate) and a file system (to store those generated pages).

## Understanding Collections

A collection defines a set of pages to generate. A collection definition exposes a list of items, the location (uri) to fetch each item, and a file path to store each item. Each collection should extend the `easygen.PublishableCollection` class.   

```
class PublishableCollection:

    def items(self):
        return []

    def location(self, obj):
        return None

    def file_path(self, obj):
        return self.location(obj)
```

`PublishableCollection` intentionally mimics django's [`Sitemap`](https://docs.djangoproject.com/en/dev/ref/contrib/sitemaps/#django.contrib.sitemaps.Sitemap) class.  

In most cases the implementation of `location()` will match `file_path()`. Some examples of collections are included further below.

## Understanding Storage

During the generation process, files need to be written somewhere. Easygen relies on django's [file storage API](https://docs.djangoproject.com/en/dev/ref/files/storage/) for this. This allows easygen to upload generated files to cloud providers that are already configured.

# Installation

```
pip install git+https://github.com/hallman76/django-easygen
```

# Configuration

Add easygen to INSTALLED_APPS in settings.py:

```
INSTALLED_APPS = [
...
    'easygen',
...
]
```

Configure easygen in settings.py:

```
EASYGEN = {
    'default': {
        'collections': ['website.collections.StaticCollection', 'blog.collections.CategoryCollection'],
        'file_system': 'django.core.files.storage.FileSystemStorage',
        'file_system_args': {'location': os.path.join(BASE_DIR, 'generated')},
    }
}
```

## Available options

| name | type | default value  |
|---|---|---|
| collections | Array of strings listing the collections that will be used | [ ] |
| file_system | String class descriptor | 'django.core.files.storage.FileSystemStorage' |
| file_system_args | Dict of options passed to file_system | {'location': os.path.join(BASE_DIR, 'generated')} |
| strip_leading_slash | Boolean| True |
| auto_index_html | Boolean | True |


## Gotchas: indexes and slashes

The options section included two settings that alter how easygen creates output: `strip_leading_slash` and `auto_index_html`. They both relate to the differences between URLs and files on disk.

`strip_leading_slash` removes the leading slash on the destination file_path. Setting this to `True` (default) allows files to be written relative to the filesystem's configuration instead of writing to the root of the filesystem.

`auto_index_html` will create index.html files and their corresponding directories for paths that end in a slash. For example:

|   |   |
|---|---| 
| `/categories/kitchen/` (trailing slash) | `categories/kitchen/index.html` |
| `/categories/kitchen` (no trailing slash) | `categories/kitchen` |

If your files don't have extensions (like in the second example) you may need to configure a mime type for them with your hosting provider.

# Generating pages

You generate static pages by running easygen's management task:

```
python manage.py easygen
```


# Alternate configurations

Easygen's configuration makes is possible to generate different sets of collections and use different file storage definitions. By default, it uses the settngs defined under `default`. Define alternate profiles and run them by passing a `--profile` argument to the manangement task.

Here's an example of multiple definitions:

```
EASYGEN = {
    'default': {
        'collections': ['website.urls.StaticCollection', 'website.urls.StateCollection'],
        'file_system': 'storages.backends.s3boto3.S3Boto3Storage',
        'file_system_args': {'location': 'static-test'},
    }
    'local': {
        'collections': ['website.collections.StaticCollection', 'blog.collections.CategoryCollection'],
        'file_system': 'django.core.files.storage.FileSystemStorage',
        'file_system_args': {'location': os.path.join(BASE_DIR, 'generated')},
    }
}
```

You can specify which settings to use by passing a `--profile` argument:

```
python manage.py easygen --profile local
```

# Example Collections

There's no strict definition of where to place collection definitions. We recommend placing them in a `collections.py` file within each app.

```
your_project
  - your_app
    - models.py
    - views.py
    - ...
    - collections.py
```

Most collections will look like the following examples. They need business logic to determine which items to expose combined with django's built in router [`reverse`](https://docs.djangoproject.com/en/dev/ref/urlresolvers/#reverse) method. 

## Example 1: Static pages

Assume a website with several pages defined in the urls.py like so:

```
from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('join', views.join, name='join'),
    path('about', views.about, name='about'),
]
```

The following collection will render each page. The dictionary `paths` allows for special treatment of the homepage.

```
from django.urls import reverse
from easygen import PublishableCollection

class StaticCollection(PublishableCollection):

    paths = {}
    paths['website:home'] = "home.html"     # override the storage path for this route

    def items(self):
        return ['website:home', 'website:join', 'website:about']

    def location(self, obj):
        return reverse(obj)

    def file_path(self, obj):
        if obj in self.paths.keys():
            return self.paths[obj]

        return reverse(obj)


```

## Example 2: data-driven pages

Assume a basic blog with articles and category pages defined in the urls.py like so:

```
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('category/<slug:category_slug>', views.articles_by_category, name='articles_by_category'),    
    path('<slug:post_slug>', views.article, name='article'),
]
```

A collection to render each category page is as follows:

```
from django.urls import reverse
from easygen import PublishableCollection
from blog import Category

class CategoryCollection(PublishableCollection):

    def items(self):
        return = Category.objects.all()

    def location(self, obj):
        return reverse('blog:articles_by_category', kwargs={'category_slug': obj.slug} )

    def file_path(self, obj):
        return reverse('blog:articles_by_category', kwargs={'category_slug': obj.slug} )

```

A collection to render each article:

```
from django.urls import reverse
from easygen import PublishableCollection
from blog import Post

class ArticleCollection(PublishableCollection):

    def items(self):
        return = Post.objects.filter(status=Post.STATUS_PUBLISHED)

    def location(self, obj):
        return reverse('blog:article', kwargs={'post_slug': obj.slug} )

    def file_path(self, obj):
        return self.location(obj)
  
```

---

Built in Boston.


