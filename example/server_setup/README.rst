=====
Setup
=====

The setup is largely based on a blog post by Graham King:
`Proxy socket.io and nginx on the same port, over SSL <http://www.darkcoding.net/software/proxy-socket-io-and-nginx-on-the-same-port-over-ssl/>`_

The end result is something similar to this:

.. image:: http://www.gliffy.com/pubdoc/4179188/L.png


Prerequisites
-------------

::

    $ sudo apt-get install libevent-dev


---------------
SSL certificate
---------------

Create a self-signed SSL certificate for the test domain django-socketio-chat.local::

    cd example/server_setup 
    ./makecrts.sh


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

Backup the original haproxy.cfg and link to our custom one::

    sudo mv /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.orig
    sudo ln -s haproxy.cfg /etc/haproxy/haproxy.cfg

TODO: Check with haproxy.cfg from the original article, it contains some other timeouts etc.
TODO: What about the check command of haproxy, we don't use it with 1.5 because it gives continuous connection
resets. 

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
