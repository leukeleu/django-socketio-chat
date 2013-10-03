# Setup

## Prerequisites

- Ubuntu
- a recent version of nginx (tested with 1.5.5)
- an SSL certificate (snake-oil or real)
- libevent-dev

    $ sudo apt-get install libevent-dev


## nginx configuration

    ...

    location /websockets/chat/ {
        proxy_pass http://localhost:8001;

        proxy_redirect             off;

        proxy_set_header           Host $host;
        proxy_set_header           X-Real-IP $remote_addr;
        proxy_set_header           X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header           X-Forwarded-Protocol https;

        proxy_read_timeout         86400s;
        proxy_send_timeout         86400s;

        proxy_http_version         1.1;
        proxy_set_header           Upgrade $http_upgrade;
        proxy_set_header           Connection "upgrade";
    }

    ...


## Links

- https://chrislea.com/2013/02/23/proxying-websockets-with-nginx/
- http://book.mixu.net/ch13.html
- http://blog.mixu.net/2011/08/13/nginx-websockets-ssl-and-socket-io-deployment/
