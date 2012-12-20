#!/bin/bash

# Create a certificate and key
mkdir -p certs && cd certs
openssl genrsa -out django-socketio-chat.key 1024
openssl req -new -key django-socketio-chat.key -out django-socketio-chat.csr  # Common Name == django-socketio-chat.local
openssl x509 -req -days 365 -in django-socketio-chat.csr -signkey django-socketio-chat.key -out django-socketio-chat.crt
chmod 600 django-socketio-chat.key
cd ..

# haproxy wants the certificat and key in one file together
cat certs/django-socketio-chat.crt certs/django-socketio-chat.key>> haproxy.pem

# cleanup 
rm -r certs
