<h1>NGINX</h1>

1. Role of NGINX

    - Reverse Proxy: NGINX is often used as a reverse proxy server that can handle requests coming from clients and forward them to the appropriate backend services (in our case, Django applications). This setup can help improve response times, manage load, and provide a single entry point for our APIs.

    - Load Balancing: NGINX can distribute incoming traffic across multiple backend servers, which can be beneficial if we're scaling our services or need to manage high traffic. SSL Termination: NGINX can handle HTTPS connections, which offloads the SSL processing from our backend applications, allowing them to focus on serving requests.

2. Complementary Architecture

    - Microservices: If we're implementing a microservices architecture, using NGINX as an API gateway to route requests to different Django services aligns with best practices. Each service can be developed independently and scaled as needed.
    - Separation of Concerns: By using NGINX, we're effectively separating concerns in our application. The backend logic remains in Django, while NGINX takes care of request handling and traffic management.

3. Project Requirements

    - If our project specifically outlines that we need to implement the backend using Django without any intermediary, then using NGINX in a way that violates those requirements could be seen as not adhering to the project guidelines. However, if the project allows or encourages or does't explicitly say that we can not use additional tools for architecture improvement, then our approach is valid.

4. Clarifying Expectations

    - Explain Your Choices: When you present your project, be prepared to explain why you chose to implement NGINX, detailing its benefits and how it complements your Django backend.

<br>

<h2> Conclusion </h2> <br>

Using NGINX as part of our architecture can greatly enhance our project's functionality and performance. Just we have to ensure that we stay aligned with the project's requirements and be ready to articulate the rationale behind our architectural decisions. If done correctly, it demonstrates our understanding of real-world application design, which is a valuable skill in software development. If you're unsure, reaching out for clarification from your instructors or peers at 42 Wolfsburg can provide further guidance.

1️⃣ user nginx;
This directive sets the user that Nginx will run as.
In this case, nginx is the system user under which the Nginx worker processes will run.
This is important for security because running Nginx as root would be a risk.
The nginx user needs proper permissions to access log files, serve static files, and communicate with other services.


2️⃣ worker_processes auto;
This directive controls how many worker processes Nginx will create.
auto means that Nginx will automatically set the number of worker processes to match the number of CPU cores available.
This improves performance because Nginx can handle multiple requests concurrently.

3️⃣ events { worker_connections 1024; }
events { ... } Block
The events block configures settings related to connections and concurrency.
worker_connections 1024;
This sets the maximum number of simultaneous connections each worker process can handle.
Since worker_processes is set to auto, the total maximum connections Nginx can handle is:
ini
Copy
Edit
total_connections = worker_processes * worker_connections
If the system has 4 CPU cores, it will create 4 worker processes.
With worker_connections 1024;, the total max connections will be:
yaml
Copy
Edit
4 * 1024 = 4096 concurrent connections
This includes all connections (e.g., client connections, proxied connections).

<h1>http {...} block</h1>

1️⃣ include /etc/nginx/mime.types;
This line tells Nginx to include the mime.types file.
The file /etc/nginx/mime.types contains mappings of file extensions to MIME types (Multipurpose Internet Mail Extensions).
It ensures that when Nginx serves files, it sets the correct Content-Type in the HTTP response headers.
Example from mime.types:
nginx
Copy
Edit
types {
    text/html    html htm shtml;
    text/css     css;
    text/xml     xml;
    image/gif    gif;
    image/jpeg   jpeg jpg;
    application/javascript js;
}
If a user requests style.css, Nginx will set:
pgsql
Copy
Edit
Content-Type: text/css

2️⃣ default_type application/octet-stream;
If Nginx does not recognize a file type, it falls back to this default MIME type.
application/octet-stream is a generic binary format.
It tells the browser:
"This is a binary file, I don't know its exact type."
Most browsers will prompt for download instead of displaying the file.
This prevents browsers from incorrectly interpreting unknown file types.

3️⃣ access_log /var/log/nginx/access.log;
This enables logging of all client requests to the access log.
The log file stores details like:
Client IP
Requested URL
HTTP status code
User-Agent
Response time
Example log entry:
swift
Copy
Edit
192.168.1.1 - - [07/Feb/2025:14:05:23 +0000] "GET /index.html HTTP/1.1" 200 1024 "-" "Mozilla/5.0"

4️⃣ error_log /var/log/nginx/error.log;
This stores errors and warnings related to Nginx.
Useful for debugging issues like:
Failed upstream connections
Misconfigured directives
Permission problems
2025/02/07 14:10:45 [error] 12345#0: *5 connect() failed (111: Connection refused) while connecting to upstream, client: 192.168.1.1, server: example.com, request: "GET /api/data HTTP/1.1"
error_log /var/log/nginx/error.log warn;
debug, info, notice, warn, error, crit, alert, emerg

What If You Don't Want Logs?
If you don’t want any logs, you can disable them like this:
error_log /dev/null crit;
Logs go to /dev/null (nowhere).
Only critical issues (crit, alert, emerg) will be logged.

<h1>http server block {...}</h1>
This block defines an HTTP server that listens on port 80 and forces all traffic to be redirected to HTTPS (port 443). Let's break it down:

listen 80 default_server;
This tells Nginx to listen for HTTP requests on port 80.
The default_server directive makes this the default virtual host when no specific server_name matches the incoming request.

listen [::]:80 default_server;
This makes the server listen on IPv6 as well.
:: is the IPv6 equivalent of 0.0.0.0 (all addresses).

server_name 10.12.12.8;
Defines the server's hostname (or IP address) that this block should respond to.
Here, it listens for requests specifically made to 10.12.12.8, which for our project transendence it represent our schools network so we can access it through schools wifi through different devices

return 301 https://$server_name$request_uri;
Redirects all incoming HTTP requests to HTTPS.
301 is a permanent redirect, telling browsers and clients to always use HTTPS.
$server_name is replaced with the actual server's hostname or IP (10.12.12.8 in this case).
$request_uri keeps the original path and query parameters intact.
Example Redirect:

http://10.12.12.8/some-page?query=123
https://10.12.12.8/some-page?query=123

<h1>https server {...} block </h1>
<h2> Evrything out of proxys blocks </h2>

listen 443 ssl default_server;
Makes Nginx listen for HTTPS requests on port 443.
ssl tells Nginx that this server block is for HTTPS.
default_server makes this the default virtual host when no specific server_name matches.

listen [::]:443 ssl default_server;
Enables listening on IPv6 for HTTPS.
[::] is the IPv6 equivalent of 0.0.0.0, meaning it accepts connections from any IPv6 address.

server_name 10.12.12.8;
Defines the host (IP or domain) this block responds to.
In this case, it's listening for HTTPS requests specifically made to 10.12.12.8.

ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
Specifies the SSL certificate file used to encrypt traffic.
This is a self-signed certificate (not issued by a trusted authority).
If a browser visits this site, it will warn that the certificate is not trusted.

ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned.key;
The private key corresponding to the SSL certificate.
This key must be kept secure because it is used to establish encrypted sessions.


6️⃣ CORS Headers
CORS (Cross-Origin Resource Sharing) controls how other domains can interact with this server.
add_header 'Access-Control-Allow-Origin' '*';
Allows any domain (*) to access resources on this server.
add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE';
add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization';
Specifies which custom headers are allowed in CORS requests.
Syntax of the Directive:
add_header → Adds an HTTP response header to tell browsers which headers are allowed in CORS requests.
Access-Control-Allow-Headers → Defines which headers the client is allowed to send in cross-origin requests.
List of headers → Each item in the list represents an HTTP header that can be sent by the client.
Detailed Explanation of Each Header Allowed
1️⃣ DNT (Do Not Track)
This header is sent by browsers to request that a website does not track the user's activity.
DNT: 1  # The user enables "Do Not Track" in their browser settings.
DNT: 0  # The user allows tracking.
Why is it allowed?
Some applications may respect DNT preferences when handling requests.
2️⃣ X-CustomHeader
A custom header that does not belong to standard HTTP headers.
Developers often use X- prefixed headers for internal APIs.
X-CustomHeader: 42Wolfsburg
Why is it allowed?
Some applications use X-CustomHeader to send custom data between frontend and backend.

3️⃣ Keep-Alive
Controls persistent connections to improve performance.
Example:
Keep-Alive: timeout=5, max=100
timeout=5 → Keep the connection open for 5 seconds.
max=100 → Allow a maximum of 100 requests before closing the connection.
Why is it allowed?
Helps in keeping a connection open between the client and server, reducing latency.

4️⃣ User-Agent
Identifies the browser or client making the request.
Example:
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36
Why is it allowed?
Some applications check the User-Agent to differentiate between mobile, desktop, or bot requests.

5️⃣ X-Requested-With
Sent by JavaScript frameworks (e.g., jQuery) in AJAX requests.
X-Requested-With: XMLHttpRequest
Why is it allowed?
Historically, used to detect AJAX requests, but now it’s mostly deprecated.

6️⃣ If-Modified-Since
Helps with caching by checking if a resource has been modified since the last request.
Example:
If-Modified-Since: Mon, 05 Feb 2024 08:00:00 GMT
Why is it allowed?
Improves performance by avoiding unnecessary downloads if the resource hasn't changed.

8️⃣ Content-Type
Specifies the format of the request body.
Example:
Content-Type: application/json
Why is it allowed?
Needed when sending JSON, XML, or form data in requests.

9️⃣ Authorization
Used for authentication in APIs.
Example:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5c...
Why is it allowed?
Allows sending JWT tokens, API keys, or OAuth tokens for authentication.

📌 Summary Table
Header	Purpose
DNT	Requests websites not to track user activity.
X-CustomHeader	Allows custom headers (internal APIs).
Keep-Alive	Helps maintain persistent connections.
User-Agent	Identifies the client/browser making the request.
X-Requested-With	Used for detecting AJAX requests (now deprecated).
If-Modified-Since	Used for caching and reducing unnecessary downloads.
Cache-Control	Controls how a resource should be cached.
Content-Type	Defines the format of request data (JSON, XML, etc.).
Authorization	Used for authentication (JWT, API keys, OAuth).

<h2>Frontend proxy -> location / {...} block</h2>
Breaking Down the Frontend Proxy Block in Nginx
This block is responsible for routing requests to your frontend service running on port 5173.

location / {
    proxy_pass http://frontend:5173;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

1️⃣ location / { ... }
What does it do?

This block matches all requests (/) coming to Nginx and routes them to the frontend service.
Example:

A request to https://10.12.12.8/ will be proxied to http://frontend:5173/.

2️⃣ proxy_pass http://frontend:5173;
What does it do?

Forwards requests to the frontend service, which is running at http://frontend:5173.
Example:

Client Request → Nginx (https://10.12.12.8/) → http://frontend:5173/
Why port 5173?

This is the default port for Vite (a frontend development server for Vue/React/etc.).
What happens if it's wrong?

If the frontend server is running on another port (e.g., 3000), this must be updated to http://frontend:3000;.

3️⃣ proxy_http_version 1.1;
What does it do?

Forces the HTTP/1.1 protocol when proxying requests.
Why is it needed?

WebSockets and keep-alive connections require HTTP/1.1.
HTTP/1.0 does not support WebSockets.

4️⃣ proxy_set_header Upgrade $http_upgrade;
What does it do?

Supports WebSockets by setting the Upgrade header.
Example WebSocket request:
Upgrade: websocket
Why is it needed?

If your frontend uses WebSockets (e.g., for real-time data), this allows the connection to be upgraded from HTTP to WebSocket.

5️⃣ proxy_set_header Connection 'upgrade';
What does it do?

Ensures the connection stays open for WebSocket communication.
Example:

Connection: upgrade
Why is it needed?

WebSockets require a persistent connection, so this header prevents disconnection.

6️⃣ proxy_set_header Host $host;
What does it do?

Sets the Host header to match the original request.
Example:
Host: 10.12.12.8
Why is it needed?

Some frontend frameworks rely on the Host header for CORS or domain-based routing.

7️⃣ proxy_cache_bypass $http_upgrade;
What does it do?

Prevents caching when upgrading connections (e.g., WebSockets).
Why is it needed?

WebSocket requests should not be cached, or else real-time communication might break.

8️⃣ proxy_set_header X-Real-IP $remote_addr;
What does it do?

Passes the client’s real IP address to the frontend.
Example:

X-Real-IP: 192.168.1.10
Why is it needed?

Useful for logging, security, and rate-limiting on the frontend side.

9️⃣ proxy_set_header X-Forwarded-For proxy_add_x_forwarded_for;
What does it do?

Passes a list of all client IP addresses through proxies.
Example:

X-Forwarded-For: 192.168.1.10, 172.16.0.1
Why is it needed?

Helps track the original client IP, even when requests pass through multiple proxies.

🔟 proxy_set_header X-Forwarded-Proto $scheme;
What does it do?

Passes the original protocol (HTTP/HTTPS) to the frontend.
Example:

X-Forwarded-Proto: https
Why is it needed?

Some frontend applications need to know if the original request was HTTPS or HTTP for redirects or security checks.

📌 Summary Table
Directive	Purpose
location / {}	Matches all requests (/) and forwards them to the frontend.
proxy_pass http://frontend:5173;	Sends requests to the frontend service running on port 5173.
proxy_http_version 1.1;	Uses HTTP/1.1 (needed for WebSockets).
proxy_set_header Upgrade $http_upgrade;	Enables WebSocket upgrades.
proxy_set_header Connection 'upgrade';	Keeps WebSocket connections open.
proxy_set_header Host $host;	Preserves the original Host header.
proxy_cache_bypass $http_upgrade;	Prevents caching for upgraded connections (WebSockets).
proxy_set_header X-Real-IP $remote_addr;	Sends the client’s real IP address to the frontend.
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;	Forwards a list of all client IPs.
proxy_set_header X-Forwarded-Proto $scheme;	Tells the frontend whether the original request was HTTP or HTTPS.