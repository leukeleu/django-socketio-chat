#!/bin/bash

sudo -v

echo "Installing haproxy 1.5"
# Normal install
sudo apt-get install haproxy

# Override normal install with custom build of 1.5
wget http://haproxy.1wt.eu/download/1.5/src/snapshot/haproxy-ss-20121204.tar.gz
tar -xvf haproxy-ss-20121204.tar.gz && cd haproxy-ss-20121204
sudo apt-get build-dep haproxy
make TARGET=linux2628 USE_STATIC_PCRE=1 USE_OPENSSL=1
sudo make install

# clean up
cd ..
rm -r haproxy-ss-20121204 && rm haproxy-ss-20121204.tar.gz 

# Make sure haproxy is enabled
sudo  sed "s/^ENABLED.*$/ENABLED=1/" -i /etc/default/haproxy 

# point init.d to our binary
sudo cp /etc/init.d/haproxy /etc/init.d/haproxy.orig
sudo sed "s/^HAPROXY.*$/HAPROXY=\/usr\/local\/sbin\/haproxy/" -i /etc/default/haproxy 
