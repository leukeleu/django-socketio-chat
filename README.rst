Socket.io - Django - HTTPS - websockets
=======================================

This project is a demonstration of how to get everything socket.io has to offer, deployed over a secure connection combined with 
the goodness of Django.

The server setup is as follows:

Internet(443) --> STunnel ---> HAProxy ---> Django 
						  		 \
						  		  ---> Socket.io 




Tested with
===========

Mac: Firefox, Chrome, Safari
Windows: ie8, Firefox
iPhone 3g: Safari