import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-easygen",
    version="1.0.0",
    author="Steve Hallman",
    author_email="hallman76@example.com",
    description="A static site generator for django.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hallman76/django-easygen",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)