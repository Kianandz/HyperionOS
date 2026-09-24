import os

if os.path.exists("/etc/nginx/sites-available"):
    IS_DEBIAN = True
    NGINX_CONF_DIR = "/etc/nginx/sites-available"
    NGINX_ENABLED_DIR = "/etc/nginx/sites-enabled"
else:
    IS_DEBIAN = False
    NGINX_CONF_DIR = "/etc/nginx/conf.d"
    NGINX_ENABLED_DIR = "/etc/nginx/conf.d"

NGINX_TEMPLATE = r"""
server {
    listen 80;
    server_name {{ domain }};
    client_max_body_size {{ max_body_size }};

    {% if site_type == 'proxy' %}
    location / {
        proxy_pass http://127.0.0.1:{{ port }};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    {% elif site_type == 'php' %}
    root {{ root_dir }};
    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_pass unix:{{ php_sock }};
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
    {% else %}
    root {{ root_dir }};
    index index.html index.htm;

    location / {
        try_files $uri $uri/ =404;
    }
    {% endif %}
}
"""

PHP_INI_PATHS = [
    "/etc/php/php.ini",
    "/etc/php/8.3/fpm/php.ini",
    "/etc/php/8.2/fpm/php.ini",
    "/etc/php.ini",
]
