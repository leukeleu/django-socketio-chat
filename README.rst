Considerations
==============

This app originates from the example chat app that came with Django Socket.io.

Because we only want to allow logged in users into the chat, there are some problems to solve:

 - The latest socket io version supports handshaking
 - The latest gevent socket io support this as well
 - The latest Django socket io does not yet

 