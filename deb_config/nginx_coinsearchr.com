server {
    server_name coinsearchr.com www.coinsearchr.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/main/CoinSearchr-site/coinsearchr.sock;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/coinsearchr.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/coinsearchr.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot


}

server {
    if ($host = www.coinsearchr.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    if ($host = coinsearchr.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    listen 80;
    server_name coinsearchr.com www.coinsearchr.com;
    return 404; # managed by Certbot




}