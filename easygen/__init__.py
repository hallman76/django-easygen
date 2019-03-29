class PublishableCollection:
    """
    Base class to define pages that will be generated. 
    """

    def items(self):
        return []

    def location(self, obj):
        """
        Returns the URI for obj. This is used to locate the appropriate view defined in urls.py. It should not include protocol/host information.
        """        
        return None

    def file_path(self, obj):
        """
        Returns the filesystem path that the generated obj should be written to. 
        """
        return self.location(obj)
