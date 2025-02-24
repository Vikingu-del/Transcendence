# NGINX

## Role of NGINX

- **Reverse Proxy**: NGINX is often used as a reverse proxy server that can handle requests coming from clients and forward them to the appropriate backend services (in our case, Django applications). This setup can help improve response times, manage load, and provide a single entry point for our APIs.
- **Load Balancing**: NGINX can distribute incoming traffic across multiple backend servers, which can be beneficial if we're scaling our services or need to manage high traffic.
- **SSL Termination**: NGINX can handle HTTPS connections, which offloads the SSL processing from our backend applications, allowing them to focus on serving requests.

## Complementary Architecture

- **Microservices**: If we're implementing a microservices architecture, using NGINX as an API gateway to route requests to different Django services aligns with best practices. Each service can be developed independently and scaled as needed.
- **Separation of Concerns**: By using NGINX, we're effectively separating concerns in our application. The backend logic remains in Django, while NGINX takes care of request handling and traffic management.

## Project Requirements

- If our project specifically outlines that we need to implement the backend using Django without any intermediary, then using NGINX in a way that violates those requirements could be seen as not adhering to the project guidelines. However, if the project allows or encourages or does not explicitly say that we cannot use additional tools for architecture improvement, then our approach is valid.

## Clarifying Expectations

- **Explain Your Choices**: When you present your project, be prepared to explain why you chose to implement NGINX, detailing its benefits and how it complements your Django backend.

## Conclusion

Using NGINX as part of our architecture can greatly enhance our project's functionality and performance. We just have to ensure that we stay aligned with the project's requirements and be ready to articulate the rationale behind our architectural decisions. If done correctly, it demonstrates our understanding of real-world application design, which is a valuable skill in software development. If you're unsure, reaching out for clarification from your instructors or peers at 42 Wolfsburg can provide further guidance.

## NGINX Configuration

### Basic Configuration

1. **user nginx;**
    - This directive sets the user that NGINX will run as. In this case, `nginx` is the system user under which the NGINX worker processes will run. This is important for security because running NGINX as root would be a risk. The nginx user needs proper permissions to access log files, serve static files, and communicate with other services.

2. **worker_processes auto;**
    - This directive controls how many worker processes NGINX will create. `auto` means that NGINX will automatically set the number of worker processes to match the number of CPU cores available. This improves performance because NGINX can handle multiple requests concurrently.

3. **events { worker_connections 1024; }**
    - The events block configures settings related to connections and concurrency. `worker_connections 1024;` sets the maximum number of simultaneous connections each worker process can handle. Since `worker_processes` is set to `auto`, the total maximum connections NGINX can handle is `worker_processes * worker_connections`.

### HTTP Block

1. **include /etc/nginx/mime.types;**
    - This line tells NGINX to include the `mime.types` file, which contains mappings of file extensions to MIME types. It ensures that when NGINX serves files, it sets the correct Content-Type in the HTTP response headers.

2. **default_type application/octet-stream;**
    - If NGINX does not recognize a file type, it falls back to this default MIME type. `application/octet-stream` is a generic binary format, which tells the browser that the file is a binary file and should be downloaded rather than displayed.

3. **access_log /var/log/nginx/access.log;**
    - This enables logging of all client requests to the access log, storing details like client IP, requested URL, HTTP status code, User-Agent, and response time.

4. **error_log /var/log/nginx/error.log;**
    - This stores errors and warnings related to NGINX, useful for debugging issues like failed upstream connections, misconfigured directives, and permission problems.

### HTTP Server Block

This block defines an HTTP server that listens on port 80 and forces all traffic to be redirected to HTTPS (port 443).

- **listen 80 default_server;**
  - This tells NGINX to listen for HTTP requests on port 80. The `default_server` directive makes this the default virtual host when no specific server_name matches the incoming request.

- **listen [::]:80 default_server;**
  - This makes the server listen on IPv6 as well.

- **server_name 10.12.12.8;**
  - Defines the server's hostname (or IP address) that this block should respond to.

- **return 301 https://$server_name$request_uri;**
  - Redirects all incoming HTTP requests to HTTPS. `301` is a permanent redirect, telling browsers and clients to always use HTTPS.

### HTTPS Server Block

This block defines an HTTPS server that listens on port 443.

- **listen 443 ssl default_server;**
  - Makes NGINX listen for HTTPS requests on port 443. `ssl` tells NGINX that this server block is for HTTPS.

- **listen [::]:443 ssl default_server;**
  - Enables listening on IPv6 for HTTPS.

- **server_name 10.12.12.8;**
  - Defines the host (IP or domain)

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




modsecurity

SecRequestBodyAccess Off or on rule

How It Works
When a client sends a request:

If the request is GET, ModSecurity only inspects the URL and headers.
If the request is POST/PUT/PATCH, ModSecurity inspects the request body for malicious payloads.
If SecRequestBodyAccess Off:

ModSecurity ignores the request body.
Attackers could bypass WAF rules by sending malicious data inside POST parameters.
If SecRequestBodyAccess On:

ModSecurity inspects the request body and applies security rules.
Malicious payloads (e.g., SQL injections, XSS, RCE) are detected and blocked.

Example Scenario
Attack Vector Without SecRequestBodyAccess On
If disabled, an attacker could send:

http
Copy
Edit
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 100

username=admin&password=' OR '1'='1  -- 
ModSecurity won’t inspect the password field, allowing SQL injection.

With SecRequestBodyAccess On
ModSecurity detects the SQL injection and blocks the request.

SecRuleEngine DetectionOnly or ON 
SecRuleEngine DetectionOnly
This directive controls how ModSecurity handles requests. The value DetectionOnly means ModSecurity analyzes traffic but does NOT block anything—it only logs suspicious activity.

Possible Values
Value	Description
On	ModSecurity is fully active—it inspects, detects, and blocks malicious requests.
Off	ModSecurity is completely disabled—no inspections, logging, or blocking.
DetectionOnly	ModSecurity detects attacks and logs them, but does not block anything.
Why Start with DetectionOnly?
When first setting up ModSecurity, running it in DetectionOnly mode ensures it doesn't accidentally block legitimate traffic.
This allows admins to review logs and fine-tune rules before enabling blocking.
Once confident that false positives are minimized, change it to On to actively block threats.


SecRequestBodyAccess on
Value: 13107200 bytes = 13 MB, If a client sends a request body larger than 13 MB, ModSecurity rejects the request.
SecRequestBodyLimit 13107200
Value: 131072 bytes = 128 KB, If a client sends a request body larger than 128 KB, ModSecurity logs the request body.
Attackers can try to send large JSON/XML payloads to overwhelm the server (e.g., XML bombs, JSON recursion attacks).
Keeping this value low prevents resource exhaustion.

SecRequestBodyLimitAction Reject
This directive defines what ModSecurity should do when a request body exceeds the limit set by SecRequestBodyLimit.

Possible Values
Value	Description
Reject	Blocks the request if the body size exceeds the limit.
ProcessPartial	Processes only the allowed portion of the body and ignores the rest.
How It Works
When a request body exceeds the limit (defined by SecRequestBodyLimit), ModSecurity follows the action specified.
With Reject, the request is immediately blocked.
With ProcessPartial, ModSecurity only processes part of the request, which might lead to incomplete or broken security checks.
✅ Best Practice: Use Reject to ensure oversized requests are blocked instead of partially processed, which could lead to security loopholes.

ecRequestBodyJsonDepth <value>
This setting limits the nesting depth of JSON objects to:

Prevent deeply nested JSON attacks (e.g., JSON bombs).
Avoid excessive CPU and memory usage when parsing JSON.
Example Configuration
apache
Copy
Edit
SecRequestBodyLimit 1048576        # Limit request body to 1MB
SecRequestBodyNoFilesLimit 131072  # Limit non-file data to 128KB
SecRequestBodyLimitAction Reject   # Block requests exceeding limits
SecRequestBodyJsonDepth 5          # Limit JSON nesting depth to 5


Update memory? “Erik's web application, Transcendence, uses JSON W...”

Yes

No
Given the specific use case for your web application Transcendence, where you're using JWTs for authentication, an API for 2FA, and WebSockets for communication, with user profiles involving 5-6 fields fetched regularly, here's a recommendation for the limits:

Suggested Limits
Request Body Size (SecRequestBodyLimit):

Since you're using JSON Web Tokens and likely handling small JSON payloads with each request, you can keep the size relatively low.
Recommended: Start with a limit of 1MB (1048576 bytes). This is usually sufficient for JWTs, JSON data, and minor profile updates. If you anticipate larger payloads (e.g., for file uploads or other heavy data), increase this as needed.
apache
Copy
Edit
SecRequestBodyLimit 1048576  # 1MB
Non-File Data Size (SecRequestBodyNoFilesLimit):

Since your requests mostly involve small fields like a username, password, and 5-6 profile fields, the non-file data size will be small.
Recommended: Keep this around 128KB (131072 bytes). This should accommodate your regular JSON requests comfortably without being too large.
apache
Copy
Edit
SecRequestBodyNoFilesLimit 131072  # 128KB
Number of Arguments (SecRequestBodyLimitAction / SecRule &ARGS):

Your request bodies are likely small with around 5-6 fields in the profile and other authentication data.
Recommended: You might want to allow around 50-100 arguments. This ensures that you're not too strict but also preventing large numbers of unnecessary or malicious parameters.
apache
Copy
Edit
SecRule &ARGS "@ge 100" \
    "id:'200007', phase:2, t:none, log, deny, status:400, \
    msg:'Failed to fully parse request body due to large argument count', severity:2"
JSON Parsing Depth (SecRequestBodyJsonDepth):

Since you're using JSON for requests, you want to limit the parsing depth to avoid deeply nested attacks.
Recommended: A depth limit of 5 or 6 should be more than sufficient for typical profile and authentication data.
apache
Copy
Edit
SecRequestBodyJsonDepth 5  # or 6, depending on your specific JSON structure
Adjusting as Needed
You can always adjust these values based on testing and real-world usage. For instance, if you start seeing legitimate requests being blocked due to these limits, you can slightly increase the limits.
Monitor logs for any false positives and adjust accordingly.
Would you like to explore any specific configuration further or dive into more advanced fine-tuning? 🚀


Explanation of the Rule:
apache
Copy
Edit
SecRule REQBODY_ERROR "!@eq 0" \
"id:'200002', phase:2,t:none,log,deny,status:400,msg:'Failed to parse request body.'"
SecRule REQBODY_ERROR "!@eq 0":
This checks the REQBODY_ERROR variable, which holds any errors related to the request body parsing.

The rule triggers if REQBODY_ERROR is not equal to 0, which indicates that an error occurred while parsing the body.
!@eq 0 is a negation (using @eq to check equality), so it will be true when REQBODY_ERROR is non-zero, meaning the body failed to parse properly.
id:'200002':
This is a unique identifier for the rule. It's used for referencing this specific rule in your logs or configuration.

phase:2:
This means the rule runs during Phase 2, which is after the request has been received and before it is sent to the backend. In Phase 2, ModSecurity checks the request body.

t:none:
This is a transformation that is applied to the data being inspected. In this case, no transformations are applied.

log:
This tells ModSecurity to log the event when the rule matches, so you can track failures in the request body parsing.

deny:
This action denies the request if the rule matches (i.e., if the request body has parsing errors).

status:400:
This specifies that a 400 Bad Request status code will be sent back to the client when the rule triggers.

msg:'Failed to parse request body.':
This is the message that will be logged when the rule triggers. It provides context, explaining that the failure occurred during request body parsing.

What This Rule Does:
This rule checks for errors during the parsing of the request body and takes the following actions:

If an error occurs while parsing the body (REQBODY_ERROR is not equal to 0), the request will be rejected, and a 400 Bad Request status will be sent back to the client.
If ModSecurity is deployed in detection-only mode, this will log the issue with a high-severity alert.
When to Use This Rule:
You should use this rule to ensure that requests are well-formed and can be parsed correctly by ModSecurity, especially when dealing with request bodies (e.g., JSON, form data, file uploads).
It's useful for identifying malformed requests that might indicate an issue with how the request body is being transmitted or an attempt to exploit your system with invalid input.
Adjustments:
If you're in detection-only mode (for example, during testing or staging), you might want to adjust the action to log instead of deny to avoid rejecting legitimate requests. In that case, you'd only log the error without blocking the request.

Example:

apache
Copy
Edit
SecRule REQBODY_ERROR "!@eq 0" \
    "id:'200002', phase:2,t:none,log,msg:'Failed to parse request body.'"
If you're using this in production, it's better to deny requests with parsing errors to protect the integrity of your application.


This rule is designed to enforce strict validation for multipart/form-data request bodies. It's typically used when processing form submissions that include files or data in multiple parts (e.g., file uploads, form submissions with multiple fields).

Explanation of the Rule:
apache
Copy
Edit
SecRule MULTIPART_STRICT_ERROR "!@eq 0" \
"id:'200003', phase:2, t:none, log, deny, status:400, \
msg:'Multipart request body failed strict validation: \
PE %{REQBODY_PROCESSOR_ERROR}, \
BQ %{MULTIPART_BOUNDARY_QUOTED}, \
BW %{MULTIPART_BOUNDARY_WHITESPACE}, \
DB %{MULTIPART_DATA_BEFORE}, \
DA %{MULTIPART_DATA_AFTER}, \
HF %{MULTIPART_HEADER_FOLDING}, \
LF %{MULTIPART_LF_LINE}, \
SM %{MULTIPART_MISSING_SEMICOLON}, \
IQ %{MULTIPART_INVALID_QUOTING}, \
IP %{MULTIPART_INVALID_PART}, \
IH %{MULTIPART_INVALID_HEADER_FOLDING}, \
FL %{MULTIPART_FILE_LIMIT_EXCEEDED}'"
SecRule MULTIPART_STRICT_ERROR "!@eq 0":
This checks the MULTIPART_STRICT_ERROR variable, which indicates if there were errors during the strict validation of the multipart request body.

!@eq 0 means that the rule will trigger if MULTIPART_STRICT_ERROR is non-zero, indicating an error in parsing or validating the multipart body.
id:'200003':
This is a unique identifier for this rule.

phase:2:
This specifies that the rule should run during Phase 2 (after the request body has been received but before it is forwarded to the backend).

t:none:
No transformation is applied to the data in this rule.

log:
Logs the event when the rule is triggered. This helps track any validation failures related to multipart data.

deny:
The request will be denied if the rule matches, preventing potentially malicious or invalid multipart data from being processed.

status:400:
If the rule triggers, a 400 Bad Request status code will be returned to the client.

msg:'Multipart request body failed strict validation':
This message is logged if the rule triggers, giving a clear explanation that the multipart data failed validation.

What the Rule Does:
This rule enforces strict validation on multipart form-data requests by checking for various potential errors during the processing of the request body.

The Error Variables in the message give more specific details about the failure:
PE: Request body processor error.
BQ: Quotation issues with boundaries.
BW: Boundary issues (e.g., extra whitespace).
DB: Data before expected boundary.
DA: Data after expected boundary.
HF: Header folding errors.
LF: Line feed errors.
SM: Missing semicolons.
IQ: Invalid quoting.
IP: Invalid multipart part.
IH: Invalid header folding.
FL: Exceeding file limit.
When to Use This Rule:
This rule is useful for rejecting malformed multipart/form-data requests that might be an attempt to exploit weak points in how multipart data is processed.
It ensures that all the individual parts in a multipart request are correctly formatted, have valid boundaries, and comply with expected standards.
Considerations:
Strict Validation: This rule is very strict. If you find that legitimate requests are being rejected due to these rules, you can switch it to detection-only mode to log the issues without rejecting requests.

Example for detection-only mode:

apache
Copy
Edit
SecRule MULTIPART_STRICT_ERROR "!@eq 0" \
  "id:'200003', phase:2, t:none, log, status:400, \
  msg:'Multipart request body failed strict validation: \
  PE %{REQBODY_PROCESSOR_ERROR}, \
  BQ %{MULTIPART_BOUNDARY_QUOTED}, \
  BW %{MULTIPART_BOUNDARY_WHITESPACE}, \
  DB %{MULTIPART_DATA_BEFORE}, \
  DA %{MULTIPART_DATA_AFTER}, \
  HF %{MULTIPART_HEADER_FOLDING}, \
  LF %{MULTIPART_LF_LINE}, \
  SM %{MULTIPART_MISSING_SEMICOLON}, \
  IQ %{MULTIPART_INVALID_QUOTING}, \
  IP %{MULTIPART_INVALID_PART}, \
  IH %{MULTIPART_INVALID_HEADER_FOLDING}, \
  FL %{MULTIPART_FILE_LIMIT_EXCEEDED}'"
Use in Production: If you're confident in the format of multipart requests and want to ensure that no malformed requests go through, keeping it as a blocking rule (with deny) is the best approach.

Summary:
This rule is used to strictly validate multipart form-data requests to ensure that they are properly formatted and conform to the expected standards. If any errors occur during validation, the request is rejected with a 400 Bad Request and an explanation of the failure.

Would you like to adjust this rule, or perhaps configure it in detection-only mode first to monitor the logs and see how it performs in your environment? Let me know if you need further guidance!


This rule is focused on detecting potential boundary errors in multipart/form-data requests. It verifies whether the multipart request body has correctly matched boundaries according to the RFC 1341 specification, which defines how multipart messages should be formatted.

Explanation of the Rule:
apache
Copy
Edit
SecRule MULTIPART_UNMATCHED_BOUNDARY "@eq 1" \
    "id:'200004', phase:2, t:none, log, deny, msg:'Multipart parser detected a possible unmatched boundary.'"
SecRule MULTIPART_UNMATCHED_BOUNDARY "@eq 1":
This checks the MULTIPART_UNMATCHED_BOUNDARY variable, which is set by ModSecurity’s multipart parser to indicate if there is an unmatched boundary. If the value is 1, it suggests that there was a mismatch between the boundaries defined in the multipart data, which may indicate a malformed or potentially malicious multipart request.

id:'200004':
This is the unique identifier for this specific rule.

phase:2:
The rule runs during Phase 2, meaning after ModSecurity has received the body of the request but before it forwards the request to the backend.

t:none:
No transformations are applied to the data in this rule.

log:
Logs an entry when the rule is triggered. This helps track the occurrence of boundary issues in multipart requests.

deny:
The request is denied if the rule matches. This helps protect against potentially malformed multipart requests that might be trying to exploit vulnerabilities in multipart data processing.

msg:'Multipart parser detected a possible unmatched boundary.':
This message is included in the log when the rule triggers. It indicates that the multipart parser detected a possible issue with unmatched boundaries in the request.

What the Rule Does:
Boundary Matching in Multipart Content:
In multipart data, boundaries are used to separate different parts (e.g., file uploads, form fields). The boundaries must be clearly defined and correctly formatted as per RFC 1341.
This rule looks for a mismatch in boundaries during the parsing of the multipart content. It checks if all the necessary boundaries are properly matched and if they follow the correct order. If any mismatched boundary is detected (with MULTIPART_UNMATCHED_BOUNDARY set to 1), the rule will block the request.

Strict vs. Permissive Mode:
The rule mentions two modes for handling boundary validation:

Strict Mode: If there are any extraneous boundary lines (i.e., any line starting with -- that isn't the start or end boundary), the request will be blocked.
Permissive Mode: If the necessary boundaries are in the correct order but there are extra lines with boundaries (which could be part of valid content like PEM files), the request will be allowed. The rule would only block requests if the boundary error is explicitly 1.
Purpose:
The rule aims to protect against malformed multipart data, which could be indicative of attempts to bypass security mechanisms or exploit vulnerabilities in the way multipart data is processed. For example, extra or incorrectly ordered boundary lines could cause an application to mishandle or fail to parse the multipart body, leading to potential vulnerabilities.

When to Use This Rule:
Blocking Malformed Multipart Data:
This rule is crucial for blocking requests that contain malformed multipart data, which could lead to vulnerabilities if mishandled.

Protection Against Exploits:
Malformed multipart content could be used in various types of attacks, such as buffer overflows or content injection. By ensuring the boundaries are correct and match the expected format, you help secure the application against these kinds of threats.

Considerations:
False Positives:
In certain situations, legitimate multipart data might contain extra boundary lines or might not strictly conform to the specification (e.g., when uploading files with internal headers). If that's the case, consider switching this rule to detection-only mode temporarily to observe any false positives before enforcing it in blocking mode.

Configuring for Specific Use Cases:
If you know your application uses multipart data that sometimes doesn’t strictly adhere to the RFC (e.g., PEM files or other formatted data), you might need to adjust this rule to a more permissive mode, as suggested in the comments within the configuration.

Example for Permissive Mode:
If you want to allow some flexibility in the multipart content but still catch critical errors, you can modify the rule as follows:

apache
Copy
Edit
SecRule MULTIPART_UNMATCHED_BOUNDARY "@eq 1" \
    "id:'200004', phase:2, t:none, log, status:400, \
    msg:'Multipart parser detected a possible unmatched boundary.'"
This would allow the request to pass even if the boundary is mismatched but will log the event for further analysis.

Summary:
This rule helps protect your application from malformed multipart/form-data requests by ensuring that boundaries are correctly matched according to the multipart specification. It is important for security, particularly when handling file uploads or complex form submissions. You should use this rule to catch and block potentially dangerous or malformed requests.

Let me know if you want more details on how to modify it for your specific use case or how to handle multipart requests more securely!


These rules in ModSecurity are related to tuning the PCRE (Perl Compatible Regular Expressions) to avoid potential denial-of-service (DoS) attacks and handling internal ModSecurity errors related to pattern matching. Let's break down the configurations and their purpose:

1. SecPcreMatchLimit and SecPcreMatchLimitRecursion
apache
Copy
Edit
SecPcreMatchLimit 1000
SecPcreMatchLimitRecursion 1000
These directives are used to set limits on how many matching operations ModSecurity can perform when processing a request. They help prevent resource exhaustion (such as CPU overuse or memory consumption) caused by overly complex regular expressions, which can be a vector for ReDoS (Regular Expression Denial of Service) attacks.

SecPcreMatchLimit 1000:
This limits the total number of matching operations (i.e., the number of times ModSecurity tries to match a regular expression during request processing). If ModSecurity attempts more than 1000 matches, it will terminate the operation to prevent an overload.

SecPcreMatchLimitRecursion 1000:
This limits the recursion depth in regular expression matching. Some regular expressions can involve deep recursive matching, which could cause excessive resource usage. This setting caps that recursion to 1000 levels.

These two settings help ensure that ModSecurity doesn’t enter into an endless loop or excessive CPU consumption due to poorly designed or maliciously crafted regular expressions.

2. Internal ModSecurity Error Handling (MSC_PCRE_LIMITS_EXCEEDED)
apache
Copy
Edit
SecRule TX:/^MSC_/ "!@streq 0" \
    "id:'200005',phase:2,t:none,log,deny,msg:'ModSecurity internal error flagged: %{MATCHED_VAR_NAME}'"
SecRule TX:/^MSC_/ "!@streq 0":
This rule checks for internal ModSecurity error flags. Specifically, it looks for any variable in the TX (transaction) collection that starts with MSC_, which indicates an internal error. The !@streq 0 part ensures the rule triggers when the variable is not equal to 0. If any internal ModSecurity error flag (such as MSC_PCRE_LIMITS_EXCEEDED) has been set, this rule will match.

id:'200005':
This is a unique ID for the rule, which ModSecurity uses to reference it.

phase:2:
The rule is evaluated during Phase 2, which means it is triggered after the request body has been received and parsed.

t:none:
No transformations are applied to the matched data (i.e., no special processing on the variables).

log:
This will log the error event whenever it occurs.

deny:
If this rule is triggered, the request is denied, preventing it from being processed further by the backend application.

msg:'ModSecurity internal error flagged: %{MATCHED_VAR_NAME}':
This is the log message that will be written when the rule is triggered. It indicates that an internal error (like an exceeded regex match limit) has been detected, and it includes the name of the matched variable (the error flag).

Purpose of These Rules:
Preventing ReDoS Attacks:
By limiting the number of regex matches and recursion, these directives prevent attackers from exploiting complex or nested regular expressions to overload the ModSecurity engine. This is particularly important for defending against ReDoS attacks, where an attacker sends specially crafted input that causes excessive computational effort for the server.

Detecting and Blocking Internal ModSecurity Errors:
The rule that checks for MSC_* flags ensures that if ModSecurity encounters an internal error (such as exceeding regex limits), it is logged and blocked. For example, if ModSecurity detects that a regex exceeded the matching limits (due to overly complex patterns or other issues), the request is blocked, and the error is logged.

When to Use These Settings:
Resource Protection:
Use these settings if your system needs to be protected from potential DoS attacks based on regex complexity. Setting appropriate match limits ensures that the server’s resources aren’t drained by malicious or malformed regular expressions.

Error Handling:
Enabling the rule for internal ModSecurity errors ensures that any internal failures (like exceeding regex match limits) are logged and denied to avoid further damage or potential exploits that might occur due to malfunctioning rules.

Possible Adjustments:
Adjusting Limits:
If your application requires more complex or extensive regular expressions, you might need to adjust the SecPcreMatchLimit and SecPcreMatchLimitRecursion values accordingly. However, make sure not to set these values too high, as doing so could undermine the protections against DoS attacks.

Handling False Positives:
If you find that legitimate requests are being blocked due to internal error flags, consider adjusting the thresholds or switching the rule from deny to alert or log to monitor the events before enforcing strict action.

Summary:
SecPcreMatchLimit and SecPcreMatchLimitRecursion are used to prevent excessive resource consumption caused by complex regular expressions.
The rule checking for MSC_ flags* ensures that any internal ModSecurity error, such as exceeding regex limits, is logged and denied.
These settings and rules help protect against potential DoS attacks and ensure ModSecurity operates efficiently without overloading the server.

Explanation of the Response Body Handling Configuration
This set of ModSecurity directives deals with the response body of the requests your server handles. It allows ModSecurity to inspect the responses coming from your web application or backend services. Let’s go over each directive and what it does:

1. SecResponseBodyAccess On
apache
Copy
Edit
SecResponseBodyAccess On
Purpose:
This directive enables ModSecurity to access the response body for inspection. ModSecurity can then inspect any data being returned by your application, such as HTML or JSON responses.

Why It's Important:
Access to the response body allows ModSecurity to detect potential security issues like:

Data leakage (sensitive information being exposed in responses).
Errors (e.g., stack traces or database errors) that could reveal information about the backend.
Injection attacks (where malicious code might be injected into the response).
Trade-off:
Enabling this directive can increase both memory consumption and response latency, as ModSecurity must buffer and inspect the response body. However, this trade-off is often worth it for the added security.

2. SecResponseBodyMimeType text/plain text/html text/xml
apache
Copy
Edit
SecResponseBodyMimeType text/plain text/html text/xml
Purpose:
This directive specifies the MIME types of responses that ModSecurity will inspect. In this case, only responses with MIME types of:

text/plain
text/html
text/xml
will be inspected by ModSecurity.

Why It’s Important:
You generally do not want ModSecurity to inspect binary files (like images, archives, etc.) since they could consume significant resources and likely do not present security risks. By limiting the inspection to document types (such as HTML, plain text, and XML), you reduce unnecessary processing while still ensuring the security of the main application response data.

3. SecResponseBodyLimit 524288
apache
Copy
Edit
SecResponseBodyLimit 524288
Purpose:
This directive sets the maximum size (in bytes) of the response body that ModSecurity will buffer and inspect. In this case, the limit is set to 524,288 bytes (or 512 KB).

Why It’s Important:
This limit helps prevent memory exhaustion caused by excessively large response bodies. If the response body exceeds this size, ModSecurity will not buffer the entire body, which helps keep memory usage in check.

Adjusting the Limit:
You can adjust this limit based on your server’s available memory and the expected size of your responses. For example, if your application often returns large JSON or HTML pages, you may need to increase this limit. If you don’t expect large responses, keeping it at 512 KB is generally fine.
4. SecResponseBodyLimitAction ProcessPartial
apache
Copy
Edit
SecResponseBodyLimitAction ProcessPartial
Purpose:
This directive tells ModSecurity what to do if a response body exceeds the SecResponseBodyLimit. The options are:

ProcessPartial: ModSecurity processes as much of the response body as it can (up to the size limit) and ignores the rest. This means ModSecurity does not block the response if it is too large but will still analyze the part of the body it can access.
Reject: This would block the entire response if it exceeds the configured size.
In this case, ProcessPartial is selected, so ModSecurity will process the response body in chunks, potentially ignoring the remainder if the response is too large.

Why It's Important:
Using ProcessPartial helps balance security with performance. By processing part of the body, ModSecurity can still catch certain malicious patterns or leakage in the response, without blocking the entire response for a large file or page. This is less strict but avoids unnecessary disruptions.

Summary of Key Points:
Response Body Access: Enabling ModSecurity to inspect response bodies allows it to detect issues such as sensitive data exposure or errors in the response.
MIME Type Filter: Only responses with the MIME types text/plain, text/html, or text/xml will be inspected. This avoids inspecting non-relevant content like images and archives.
Response Size Limiting: The body of responses larger than 512 KB will not be fully buffered and analyzed, preventing excessive memory usage. Instead, ModSecurity processes as much of the response as it can.
Partial Response Processing: If a response exceeds the body size limit, ModSecurity will process the parts it can and let the rest pass through, rather than rejecting the whole response. This provides a balance between security and usability.
Possible Adjustments:
If you need to inspect larger responses: You can increase the SecResponseBodyLimit to a higher value, especially if your application returns larger JSON payloads, for example.

If you want stricter handling of large responses: You could change SecResponseBodyLimitAction to Reject if you want to block any response that exceeds the limit.

Performance Considerations: Enabling response body inspection increases memory usage and latency. Ensure that the increase in security is balanced against the potential impact on performance, particularly if you're handling large amounts of traffic or large response bodies.


The configuration you've provided for SecTmpDir and SecDataDir defines the temporary directories where ModSecurity stores files and persistent data. Here's a breakdown of each directive:

1. SecTmpDir /tmp/
Purpose: This specifies the location where ModSecurity will store temporary files. These could be used for things like processing file uploads that exceed size limits.

Security Consideration: The default /tmp/ directory is world-writable, meaning any process on the system could potentially read or write to this directory, which is a security concern. Therefore, it’s recommended to change this to a private location to avoid exposing sensitive data.

Best Practice:

Set SecTmpDir to a directory that only your web server or ModSecurity process can access, like /var/cache/modsec_tmp/ or /opt/modsec_tmp/, and make sure this directory has the appropriate permissions set (e.g., chmod 700).
Example:

bash
Copy
Edit
SecTmpDir /var/cache/modsec_tmp/
2. SecDataDir /tmp/
Purpose: This specifies the location where ModSecurity will store persistent data, such as audit logs and other operational data.

Security Consideration: Similar to SecTmpDir, the /tmp/ directory is generally accessible by all users, which is not ideal for sensitive ModSecurity data. The directory used here should be private to ensure that sensitive information is not accessible by unauthorized users.

Best Practice:

Change SecDataDir to a more secure location. A directory that is only accessible by your web server or ModSecurity should be selected. Ensure that this directory is not world-writable and has the correct permissions set.
Example:

bash
Copy
Edit
SecDataDir /var/cache/modsec_data/
Permissions and Security Considerations:
After choosing the appropriate directories, make sure that only the user running ModSecurity (usually the web server user) has write and read access to the directories.

For example, if your web server runs under the user www-data (common for Apache or Nginx), set the appropriate permissions:

bash
Copy
Edit
chown -R www-data:www-data /var/cache/modsec_tmp/
chown -R www-data:www-data /var/cache/modsec_data/
chmod 700 /var/cache/modsec_tmp/
chmod 700 /var/cache/modsec_data/
This will ensure that the ModSecurity temporary and persistent data directories are both secure and restricted to the appropriate processes.

Summary:
For Transcendence (or any other web application), it's essential to:

Change the default SecTmpDir and SecDataDir from /tmp/ to a more secure location.
Ensure proper permissions to limit access to these directories to only the user running ModSecurity or the web server.
By following these practices, you will reduce the risk of unauthorized access to sensitive ModSecurity data and improve your web application's security posture.

The configuration you've posted relates to how ModSecurity handles file uploads. It specifies where to store intercepted files, whether to keep those files, and how to handle file permissions. Here's a breakdown of each part:

1. SecUploadDir /opt/modsecurity/var/upload/
Purpose: This directive defines the location where ModSecurity will store uploaded files that it intercepts. These are typically files that were part of a web request (like file uploads) that ModSecurity is processing. It's crucial that this directory is private, meaning only ModSecurity or the web server user has access to it.

Best Practice:

Like the previous temporary directories, it's important to choose a secure, private location for this directory. You can store uploaded files in a dedicated directory such as /var/cache/modsec_upload/ or /opt/modsec_uploads/, making sure it's inaccessible to other users.
Example:

bash
Copy
Edit
SecUploadDir /var/cache/modsec_upload/
This way, you ensure that uploaded files are stored securely and cannot be accessed by unauthorized users.

2. SecUploadKeepFiles RelevantOnly
Purpose: This directive controls whether ModSecurity should keep the uploaded files. By default, ModSecurity may discard files that are not flagged as suspicious or unusual. This directive ensures that only relevant files are kept for further analysis or inspection.

Best Practice:

If you don't need to keep every uploaded file, this is a good setting. However, if you need to retain files for post-processing or auditing, you could change this directive to "Always" or adjust it based on your specific requirements.
Example:

bash
Copy
Edit
SecUploadKeepFiles Always
Alternatively, if you only need files that are flagged for suspicion, you can leave it as is (which is generally recommended for most use cases).

3. SecUploadFileMode 0600
Purpose: This directive defines the permissions for files that are uploaded and stored by ModSecurity. The default permission is 0600, which means that only the owner (usually the ModSecurity or web server process) can read and write the file. This is a secure setting because no other users on the system can access the uploaded file.

Best Practice:

The default setting of 0600 is generally appropriate for security purposes. If you're planning to interface ModSecurity with an external program (e.g., for scanning files with an antivirus program), you might need to relax the permissions slightly. However, if no such external program is involved, keeping 0600 is the most secure choice.
Example (if needed for external programs):

bash
Copy
Edit
SecUploadFileMode 0640
This would allow the ModSecurity process to read and write the file, while also allowing read access for a group (e.g., an antivirus service), but write access would be restricted.

Summary:
For Transcendence (or any web application), the recommendations are:

Choose a private directory for uploaded files, such as /var/cache/modsec_upload/ or /opt/modsec_uploads/, and make sure only ModSecurity and the web server have access to it.

Example:

bash
Copy
Edit
SecUploadDir /var/cache/modsec_upload/
Configure the retention of uploaded files based on your needs. The default of "RelevantOnly" is generally a good choice unless you want to keep all files for auditing or further processing.

Example:

bash
Copy
Edit
SecUploadKeepFiles Always
Set secure file permissions. Unless you need to interface with an external program, it's best to keep the default setting of 0600.

Example (if needed for integration with external tools):

bash
Copy
Edit
SecUploadFileMode 0640
This configuration ensures the security and proper handling of file uploads in your Transcendence web application.

The debug log configuration in ModSecurity controls how detailed the logs are for troubleshooting and monitoring. Here’s an explanation of each directive:

1. SecDebugLog /opt/modsecurity/var/log/debug.log
Purpose: This directive specifies the location where the debug logs will be stored. When enabled, it provides detailed logs about the ModSecurity actions, which can be extremely helpful during troubleshooting.

Best Practice:

You should specify a secure, private location for your debug logs. Since these logs can contain sensitive information about requests, headers, and body content, they should not be accessible to unauthorized users. A good location could be /var/log/modsec_debug/ or /opt/modsec_debug/.
Example:

bash
Copy
Edit
SecDebugLog /var/log/modsec_debug/debug.log
2. SecDebugLogLevel 3
Purpose: This directive sets the level of detail for debug logs. The value ranges from 0 (minimal logging) to 9 (maximum verbosity). The higher the level, the more detailed the logs will be.

Best Practice:

For normal operations, you typically don’t want to log at the highest level because it can generate very large log files and may impact server performance. Level 3 is often sufficient for troubleshooting, as it provides a balance of detail without overwhelming the logs with excessive information.
In production, consider lowering the log level to avoid excessive output. You can use level 2 or even 1 after resolving issues in the initial setup phase.
Example (for regular troubleshooting):

bash
Copy
Edit
SecDebugLogLevel 3
Example (for production):

bash
Copy
Edit
SecDebugLogLevel 1
Summary for Transcendence:
Set the debug log location to a secure path like /var/log/modsec_debug/ to ensure the logs are stored privately.
Use SecDebugLogLevel 3 during development or debugging, and lower the level to 1 or 2 in production to avoid excessive log file sizes and minimize performance impact.
Example configuration:

bash
Copy
Edit
SecDebugLog /var/log/modsec_debug/debug.log
SecDebugLogLevel 3
This setup will provide sufficient detail for troubleshooting without overwhelming the system with excessive logging in production.


Here’s an explanation of each directive in the Audit Log Configuration section, along with recommendations for your Transcendence project:

1. SecAuditEngine RelevantOnly
Purpose: This setting controls what type of transactions are logged. When set to RelevantOnly, ModSecurity will log only transactions that are deemed relevant, i.e., those that trigger rules or have a server error.

Best Practice:

This is typically a good setting to use because it prevents unnecessary logging for benign requests (like 404s) and focuses on the ones that matter—those that trigger security rules or result in errors.
For development or debugging purposes, you can switch it to On to log all transactions, but for production, RelevantOnly is recommended.
Example:

bash
Copy
Edit
SecAuditEngine RelevantOnly
2. SecAuditLogRelevantStatus "^(?:5|4(?!04))"
Purpose: This defines which HTTP status codes will trigger an audit log entry. Here, the configuration specifies logging for status codes starting with 5 (server errors) or 4xx (client errors), except for 404 (Not Found). The ^(?:5|4(?!04)) is a regular expression used to match these codes.

Best Practice:

The default setting is good because it focuses on errors while excluding common non-errors like 404s, which are often harmless.
Example:

bash
Copy
Edit
SecAuditLogRelevantStatus "^(?:5|4(?!04))"
3. SecAuditLogParts ABIJDEFHZ
Purpose: This directive specifies which parts of the request and response should be logged. The parts listed here are:
A: Request headers
B: Response body
I: Request body
J: Request arguments (parameters)
D: Response headers
E: Environment variables
F: Files uploaded (if any)
H: HTTP request line (method, URI, protocol)
Z: A special marker for the end of the log entry
Best Practice:
This configuration logs a broad set of data, which can be helpful for detailed security analysis but can also result in large log files.
You can adjust this list to log only the parts you care about, depending on the level of detail needed. For example, if you don’t care about request bodies or environment variables, you could remove those from the list.
Example (to exclude body logs):
bash
Copy
Edit
SecAuditLogParts ABJDEFHZ
4. SecAuditLogType Serial
Purpose: This directive specifies how the audit logs should be written. Serial means that all log entries for a single transaction will be written to the same file, making it easier to view related entries.

Best Practice:

Serial logging is the most common and makes it easier to view the logs in one place. However, if you expect a very high volume of traffic and need better performance, you can use Concurrent logging to write logs in parallel.
Example:

bash
Copy
Edit
SecAuditLogType Serial
5. SecAuditLog /var/log/modsec_audit.log
Purpose: This specifies the location where the audit log should be written.

Best Practice:

The file path /var/log/modsec_audit.log is a good default for storing the logs, but you may want to ensure that it’s stored in a location with adequate disk space and is protected from unauthorized access.
Consider rotating your logs regularly if the application gets a lot of traffic.
Example:

bash
Copy
Edit
SecAuditLog /var/log/modsec_audit.log
6. SecAuditLogStorageDir /opt/modsecurity/var/audit/
Purpose: This directive specifies the directory where concurrent audit logs should be stored. Since it’s commented out, it’s not being used by default. It’s only relevant if you choose to use Concurrent logging.

Best Practice:

This is only relevant if you opt for Concurrent logging. In that case, specify a secure and private directory with appropriate disk space.
Summary for Transcendence:
For Transcendence, I would recommend the following configuration, assuming you're using RelevantOnly for logging and want detailed transaction logs:

bash
Copy
Edit
Log only relevant transactions and exclude common 404 errors
SecAuditEngine RelevantOnly
SecAuditLogRelevantStatus "^(?:5|4(?!04))"

Log essential parts of the request and response
SecAuditLogParts ABIJDEFHZ

Use serial logging to group all logs for a single transaction
SecAuditLogType Serial
SecAuditLog /var/log/modsec_audit.log
This configuration ensures you're capturing important security events and errors, while avoiding excessive logs from harmless requests. It provides a balance between visibility into potential security threats and maintaining manageable log sizes.


Here’s an explanation of each directive in the Miscellaneous section, along with recommendations for your Transcendence project setup:

1. SecArgumentSeparator &
Purpose: This defines the character used to separate parameters in an application/x-www-form-urlencoded request. The default separator is &, which is the most commonly used separator in web applications.

Best Practice:

& is the standard separator for form parameters and is suitable for most web applications. Unless you know your application uses a different separator, this is the correct configuration.
Example:

bash
Copy
Edit
SecArgumentSeparator &
2. SecCookieFormat 0
Purpose: This specifies the format of cookies. Format 0 is the most commonly used format for cookies, where the cookie name and value are separated by an equal sign (=) and each cookie is separated by a semicolon (;).

Best Practice:

Format 0 is generally used by most web applications. Setting this option ensures ModSecurity handles cookies in the expected way and helps avoid evasion attacks.
Example:

bash
Copy
Edit
SecCookieFormat 0
3. SecUnicodeMapFile unicode.mapping 20127
Purpose: This directive specifies a file that contains a mapping for Unicode characters. The mapping helps ModSecurity correctly decode URL-encoded data, which can include characters from different languages and character sets.

Best Practice:

The unicode.mapping file and character encoding specified (in this case, 20127) help ensure ModSecurity properly handles different character sets. Unless you have specific needs, this setting should be left as is.
Ensure the file exists and points to the correct Unicode mapping for your environment.
Example:

bash
Copy
Edit
SecUnicodeMapFile unicode.mapping 20127
4. SecStatusEngine Off
Purpose: This controls whether ModSecurity will send status information (like the version of ModSecurity, Web Server version, etc.) to external parties. When set to Off, no status information is shared.

Best Practice:

Off is the recommended setting as it prevents ModSecurity from sharing unnecessary information that could potentially be used in attacks. It also reduces any unnecessary overhead.
Example:

bash
Copy
Edit
SecStatusEngine Off
Summary for Transcendence:
For Transcendence, your configuration could look like this, as it ensures you’re using standard settings for parameter separation, cookies, and Unicode decoding:

bash
Copy
Edit
Use the default argument separator (&) for form parameters
SecArgumentSeparator &

Use the standard cookie format (0)
SecCookieFormat 0

Specify the Unicode mapping for decoding
SecUnicodeMapFile unicode.mapping 20127

Disable ModSecurity status reporting
SecStatusEngine Off
This configuration is optimal for your setup, ensuring that ModSecurity properly handles form submissions, cookies, and encoding, while avoiding unnecessary exposure of server information.


Additional rules
SecRule REQUEST_HEADERS:Content-Type "^application/[a-z0-9.-]+[+]json" \
    "id:'200006',phase:1,t:none,t:lowercase,pass,nolog,ctl:requestBodyProcessor=JSON"

1. SecRule → Defines a security rule in ModSecurity
2. REQUEST_HEADERS:Content-Type → This checks the Content-Type header of incoming HTTP requests.
3. "^application/[a-z0-9.-]+[+]json" → This is a regular expression (regex) that matches:
        Any application/ media type that ends with +json, such as:
        application/ld+json
        application/vnd.api+json
        application/geo+json
    The regex breakdown:
        application/ → Ensures it starts with application/
        [a-z0-9.-]+ → Matches characters allowed in the media type (letters, numbers, dot, and hyphen)
        [+]json → Ensures that it ends with +json
4. id:'200006' → Assigns a unique rule ID (200006).
5. phase:1 → The rule is applied in Phase 1 (request headers processing).
6. t:none,t:lowercase → No transformations (t:none), but t:lowercase ensures case insensitivity.
7. pass,nolog → The rule does not block or log the request, it just passes through.
7. ctl:requestBodyProcessor=JSON → Enables JSON request body parsing in ModSecurity for these   media types.

Why This Rule Matters?
Normally, ModSecurity only enables JSON request body parsing for Content-Type: application/json.
However, APIs and applications sometimes use custom JSON-based MIME types (e.g., application/ld+json).
This rule expands the JSON processor to handle all +json subtypes.


