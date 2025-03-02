server {
        listen 80;
        listen [::]:80;
        server_name vault;
        return 301 https://$host$request_uri;
    }

    # Add this server block after your existing server blocks
    server {
        listen 443 ssl;
        listen [::]:443 ssl;
        server_name vault;

        # Use the same SSL certificates
        ssl_certificate /tmp/nginx/ssl/nginx-selfsigned.crt;
        ssl_certificate_key /tmp/nginx/ssl/nginx-selfsigned.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        
        # Direct proxy to Vault without path manipulation
        location / {
            proxy_pass http://vault:8200/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

     server {
        listen 80;
        listen [::]:80;
        server_name grafana;
        return 301 https://$host$request_uri;
    }

    # Add this server block after your existing server blocks
    server {
        listen 443 ssl;
        listen [::]:443 ssl;
        server_name grafana;

        # Use the same SSL certificates
        ssl_certificate /tmp/nginx/ssl/nginx-selfsigned.crt;
        ssl_certificate_key /tmp/nginx/ssl/nginx-selfsigned.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        
        # Direct proxy to Vault without path manipulation
        location / {
            proxy_pass http://grafana:3000/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
