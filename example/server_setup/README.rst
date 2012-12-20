=====
Setup
=====

The setup is largely based on a blog post by Graham King:
`Proxy socket.io and nginx on the same port, over SSL <http://www.darkcoding.net/software/proxy-socket-io-and-nginx-on-the-same-port-over-ssl/>`_

The end result is something similar to this:

.. image:: http://www.darkcoding.net/files/2011/12/socketio_web_same_port.png


Prerequisites
-------------

::

    $ sudo apt-get install libevent-dev


---------------
SSL certificate
---------------

Create a self-signed SSL certificate for the test domain django-socketio-chat.local.

::

    mkdir certs && cd certs
    openssl genrsa -out django-socketio-chat.key 1024
    openssl req -new -key django-socketio-chat.key -out django-socketio-chat.csr  # Common Name == django-socketio-chat.local
    openssl x509 -req -days 365 -in django-socketio-chat.csr -signkey django-socketio-chat.key -out django-socketio-chat.crt
    chmod 600 django-socketio-chat.key


-----------
HAProxy 1.5
-----------

Installation (Ubuntu)
---------------------

Install HAProxy 1.5 by running the bootstrap script::

    cd example/server_setup
    sudo ./bootsrap_ubuntu.sh


Configuration
-------------

::

    sudo cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.orig
    sudo nano -w /etc/haproxy/haproxy.cfg


Copy the contents of `server_setup/haproxy.cfg` into the file for a minimal configuration.
TODO: check with haproxy.cfg from the original article, it contains some other timeouts etc.


-------
Testing
-------

::

    sudo /etc/init.d/haproxy start


Add django-socketio-chat.local to your local /etc/hosts file.


-------------
Other sources
-------------

* `http://book.mixu.net/ch13.html <http://book.mixu.net/ch13.html>`_
* `http://blog.mixu.net/2011/08/13/nginx-websockets-ssl-and-socket-io-deployment/ <http://blog.mixu.net/2011/08/13/nginx-websockets-ssl-and-socket-io-deployment/>`_
