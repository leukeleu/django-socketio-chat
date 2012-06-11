 http://book.mixu.net/ch13.html
 http://blog.mixu.net/2011/08/13/nginx-websockets-ssl-and-socket-io-deployment/
    

 we need latest (1.4) haproxy <http://www.gubatron.com/blog/2011/04/06/have-the-latest-haproxy-as-a-ubuntu-service/>


# Install stunntel4

    sudo apt-get install stunnel

Copy the contents of stunnel.conf /etc/stunnel/stunnel.conf

Modify the ‘ENABLED=0′ line to ‘ENABLED=1′

    sudo nano /etc/default/stunnel


# Install haproxy 1.4

[Source](http://www.networkinghowtos.com/howto/compile-haproxy-from-source-on-ubuntu/)

First normally install the latest haproxy with apt-get
    
    sudo apt-get install haproxy

This will have installed 1.3, but we want 1.4. We will only be re-using the init.d script so we can run our
manually compiled haproxy as a service.

Downoad and extract haproxy 1.4

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
