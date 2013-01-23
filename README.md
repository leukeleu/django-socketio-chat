# Django - Socket.IO - Tornadio2 - chat over HTTPS

This project is a basic implementation of a Socket.IO chat application, over HTTPS,
integrated with Django user management.

The server setup is as follows:

                                 ┌─[ 8000 ]-> Django
                                 │
    Internet -[ 443 ]-> HAProxy ─┤
                                 │
                                 └─[ 8001 ]-> Socket.io

**Note** This project comes with an example HAProxy configuration which listens on port 8443.

HAProxy takes care of ssl encryption and proxying. All socket.io related requests are proxied to
a small tornadio server.


## Setup

Follow the instructions in `example/server_setup/README.md`

    pip install ./django-socketio-chat

Create the d-socketio-chat database, and sync it.

    cd example
    python manage.py syncdb


## Running

1. start Django

    cd example
    python manage.py runserver 0:8000

2. start the tornadio app

    python server.py


## Customization

### Limiting users

You can configure who sees who with two callbacks that take a `user` object and return a queryset of users.
By default all users are allowed to chat with anybody.

The example setting below illustrates this:

   DJANGO_SOCKETIO_CHAT = {                                                                                           |~                                                                                                                     
        'users_that_i_see': permissions.users_that_i_see,                                                              |~                                                                                                                     
        'users_that_see_me': permissions.users_that_see_me                                                             |~                                                                                                                     
    } 

