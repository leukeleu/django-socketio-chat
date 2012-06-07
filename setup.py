from setuptools import setup, find_packages


setup(
    name = "django-socketio-chat",
    version = __import__("django_socketio_chat").__version__,
    author = "Marko Tibold",
    author_email = "mtibold@leukeleu.nl",
    description = ("A Django chat app built on Django-socketio"),
    long_description = open("README.rst").read(),
    #url = "http://github.com/stephenmcd/django-socketio",
    py_modules=["django_socketio_chat",],
    install_requires=["django-socketio"],
    zip_safe = False,
    include_package_data = True,
    packages = find_packages(),
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
    ]
)