Django - Socket.IO - Tornadio2 - chat over HTTPS
================================================

This project is a basic implementation of a Socket.IO chat application, over HTTPS,
integrated with Django user management.

The server setup is as follows:

::

                                                   ┌─[ 8000 ]-> Django
                                                   │
    Internet -[ 443 ]-> stunnel -[ 81 ]-> HAProxy ─┤
                                                   │
                                                   └─[ 8001 ]-> Socket.io


Tested with
-----------

- Mac: Firefox, Chrome, Safari
- Windows: IE8, Firefox
- iPhone 3G: Safari


Example project
---------------

::

    cd example

Follow the instructions in `server_setup/README.rst`

::

    pip install -r requirements.txt
    pip freeze

::

    Django==1.4.2
    MySQL-python==1.2.4b5
    TornadIO2==0.0.4
    django-templatetag-handlebars==1.2.0
    simplejson==2.6.2
    tornado==2.4
    wsgiref==0.1.2


Also make sure the django_socketio_chat package can be found, by adding its parent folder to a .pth file in site-packages.

::

    cdvirtualenv
    cd lib/python2.6/site-packages/
    nano -w django-socketio-chat.pth

::

    /path/to/django-socketio-chat/


Create the d-socketio-chat database, and sync it.

::

    python manage.py syncdb


Running
-------

1. start Django

::

    python manage.py runserver 0:8000


2. start the tornadio app

::

    cd tornadio_app
    python chat.py
