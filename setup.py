from setuptools import setup, find_packages

setup(
    name = "django-socketio-chat",
    version = __import__("django_socketio_chat").__version__,
    author = "Dennis Bunskoek, Niels van Dijk, Marko Tibold",
    author_email = "info@leukeleu.nl",
    description = ("A Django chat app built on Tornadio2. Requires HAProxy"),
    long_description = open("README.md").read(),
    url = "http://github.com/leukeleu/django-socketio-chat",
    py_modules=["django_socketio_chat",],
    install_requires=["djangorestframework>=2.1.15",
                      "django-uuidfield==0.4.0",
                      "TornadIO2==0.0.4"],
    zip_safe = False,
    include_package_data = True,
    packages = find_packages(),
    classifiers = [
            "Development Status :: 4 - Beta",
            "Environment :: Web Environment",
            "Framework :: Django, SocketIO",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: POSIX",
            "Programming Language :: Python",
            "Topic :: Internet :: WWW/HTTP",
            "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
            "Topic :: Internet :: WWW/HTTP :: WSGI",
        ]
)

