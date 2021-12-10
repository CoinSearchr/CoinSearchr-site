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

    access_log /var/log/nginx/coinsearchr.com.access.log;

    client_max_body_size 100M;
    charset utf-8;

    listen 127.0.0.1:8080; # for Tor Hidden Service
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

# Created for HTTPS Dev
server {
    server_name coinsearchr.com www.coinsearchr.com;

    location / {
        include proxy_params;
        proxy_pass http://localhost:5000;
    }

    listen 5001 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/coinsearchr.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/coinsearchr.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}

## AWSTATS

server {
    server_name awstats.coinsearchr.com;

    root    /var/www/awstats.coinsearchr.com;
    error_log /var/log/nginx/awstats.coinsearchr.com.error.log;
    access_log off;
    log_not_found off;

#    listen 80; # managed by Certbot

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/awstats.coinsearchr.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/awstats.coinsearchr.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot


    location ^~ /icon {
        alias /usr/share/awstats/icon/;
    }

    location ^~ /awstats-icon {
        alias /usr/share/awstats/icon/;
    }


    location ~ ^/cgi-bin/.*\\.(cgi|pl|py|rb) {
        auth_basic            "AWStats Admin - Please Login";
        auth_basic_user_file  awstats.htpasswd;

        gzip off;
        include         fastcgi_params;
        fastcgi_pass unix:/var/run/php/php7.4-fpm.sock; # change this line if necessary
        fastcgi_index   cgi-bin.php;
        fastcgi_param   SCRIPT_FILENAME    /etc/nginx/cgi-bin.php;
        fastcgi_param   SCRIPT_NAME        /cgi-bin/cgi-bin.php;
        fastcgi_param   X_SCRIPT_FILENAME  /usr/lib$fastcgi_script_name;
        fastcgi_param   X_SCRIPT_NAME      $fastcgi_script_name;
        fastcgi_param   REMOTE_USER        $remote_user;
    }



}

