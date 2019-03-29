import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.http import HttpRequest
from django.urls import resolve
from django.urls.exceptions import NoReverseMatch
from django.utils.module_loading import import_string

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generates static html based on a series of collections'

    def add_arguments(self, parser):
        parser.add_argument('--profile', default='default',required=False)

    def handle(self, *args, **options):

        if not hasattr(settings, 'EASYGEN'):
            self.stdout.write(self.style.NOTICE('No EASYGEN setting defined.'))
            return

        fs = None
        
        config = settings.EASYGEN.get(options['profile'], {})

        collections = config.get('collections', [])
        file_system = config.get('file_system', 'django.core.files.storage.FileSystemStorage')
        file_system_args = config.get('file_system_args', {'location': os.path.join(settings.BASE_DIR, 'generated')})
        strip_leading_slash = config.get('strip_leading_slash', True)
        auto_index_html = config.get('auto_index_html', True)

        logger.debug("Using collections: {}".format(collections))
        logger.debug("Using file_system: {}".format(file_system))
        logger.debug("Using file_system_args: {}".format(file_system_args))
        logger.debug("Using strip_leading_slash: {}".format(strip_leading_slash))
        logger.debug("Using auto_index_html: {}".format(auto_index_html))

        fs = import_string(file_system)(**file_system_args)



        if (len(collections)) == 0:
            self.stdout.write(self.style.NOTICE('No collections defined.'))
            
        for collection_string in collections:
            logger.debug("Processing collection: {}".format(collection_string))

            try:
                instance = import_string(collection_string)()
                items = instance.items()
                try:
                    iterator = iter(items)
                except TypeError:
                    self.stderr.write("Invalid items in collection definition (not iterable)")
                    items = []

                for item in items:
                    try:
                        logger.debug("Processing item: {}".format(item))

                        uri = instance.location(item)
                        if uri is not None and len(uri) > 0:
                            # using the built-in router, get the view method for this uri
                            view, args, kwargs = resolve(uri)

                            request = HttpRequest()

                            kwargs['request'] = request
                            response = view(*args, **kwargs) 
                            
                            path = instance.file_path(item)
                            if path is not None and len(path) > 0:
                                if path.startswith('/') and strip_leading_slash:
                                    path = path[1:]

                                if len(path) == 0 and auto_index_html:
                                    path += "index.html"

                                if path.endswith('/') and auto_index_html:
                                    path += "index.html"

                                try:
                                    fs.delete(path)
                                    fs.save(path, ContentFile(response.content))
                                except Exception as e:
                                    self.stderr.write(str(e))
                                    self.stderr.write("path: {}".format(path))

                            else:
                                self.stderr.write("Invalid file_path for URI {}".format(uri))
                        else:
                            self.stderr.write("Invalid URI for: {}".format(item))

                    except NoReverseMatch as e:
                        self.stderr.write(str(e))

            except ImportError as e:
                self.stderr.write(str(e))
            except AttributeError as e:
                self.stderr.write(str(e))


        self.stdout.write(self.style.SUCCESS('Done'))
        


