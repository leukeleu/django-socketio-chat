# Setup

The setup is based on the idea of [Graham King](http://www.darkcoding.net/software/proxy-socket-io-and-nginx-on-the-same-port-over-ssl/)

It will look somewhat like this:

![image](http://www.darkcoding.net/files/2011/12/socketio_web_same_port.png)

# Install stunnel4

First create an ssh certificate and key if you don't have one yet:
    
    openssl genrsa -out mysite.key 1024
    openssl req -new -key mysite.key -out mysite.csr  # common name == your domain
    openssl x509 -req -days 365 -in mysite.csr -signkey mysite.key -out mysite.crt

Install stunnel:

    sudo apt-get install stunnel

Copy the contents of stunnel.conf /etc/stunnel/stunnel.conf

Modify the ‘ENABLED=0′ line to ‘ENABLED=1′

    sudo nano /etc/default/stunnel

Make sure the config points to the right sever certificate and private key.


# Install haproxy 1.4

[Source](http://www.networkinghowtos.com/howto/compile-haproxy-from-source-on-ubuntu/)

First normally install the latest haproxy with apt-get
    
    sudo apt-get install haproxy

This will have installed 1.3 if you are running Ubuntu 10.4, but we want 1.4. We will only be re-using the init.d script so we can run our
manually compiled haproxy as a service.

## Download and extract haproxy 1.4 

skip this step if you are running Ubuntu 11.04+

    wget http://haproxy.1wt.eu/download/1.4/src/haproxy-1.4.21.tar.gz

    tar -xvf haproxy-1.4.21.tar.gz && cd haproxy-1.4.21

    make TARGET=linux26

    sudo make install


Modify the ‘ENABLED=0′ line to ‘ENABLED=1′

    sudo nano /etc/default/haproxy


Edit the startup script to tell it where the newly compiled haproxy binary is located.

     sudo nano /etc/init.d/haproxy

Change HAPROXY to:

    HAPROXY=/usr/local/sbin/haproxy

# Configure haproxy

Copy the contents from haproxy.cfg to /etc/haproxy/haproxy.cfg 

Other sources:

 http://book.mixu.net/ch13.html
 
 http://blog.mixu.net/2011/08/13/nginx-websockets-ssl-and-socket-io-deployment/
