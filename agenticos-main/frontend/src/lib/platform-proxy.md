# **Understanding&#x20;**`platformProxy()`**&#x20;— the central API proxy**

This code is a very important part of your Next.js platform architecture.

It implements a **Backend-for-Frontend (BFF)** pattern.

The main idea is:

> The frontend does not communicate directly with the FastAPI backend. Instead, every API request passes through one Next.js server-side route that handles authentication, organization context, request forwarding, and response forwarding.

Let's understand the concepts first, then go through the code step by step.

## **1. The big picture: what problem does this solve?**

Imagine your platform has these features:

- AI agents
- Agent runs
- Approvals
- Knowledge base
- RAG
- Skills
- Providers
- Roles
- Organization sharing

Your frontend might need to call many backend endpoints:

```
/api/v1/agents
/api/v1/agents/123
/api/v1/runs
/api/v1/approvals
/api/v1/skills
/api/v1/providers
/api/v1/roles
/api/v1/kb
/api/v1/rag
```

Your backend is FastAPI, and your frontend is Next.js.

A simple architecture would be:

**Browser**

React components / JavaScript

**Next.js API Proxy**

Authentication · Organization · Forwarding

**FastAPI Backend**

Business logic · Database · Permissions

The browser calls:

```
https://your-platform.com/api/agents
```

Next.js forwards the request to:

```
http://localhost:8000/api/v1/agents
```

The browser never needs to know that the backend is running on port 8000.

### **Why not let the browser call FastAPI directly?**

There are several reasons.

**1. Security**

The access token is stored in an `HttpOnly` cookie. JavaScript cannot read that cookie directly.

**2. Hide backend infrastructure**

The backend URL stays on the server and is not included in the frontend JavaScript bundle.

**3. Centralize authentication**

Instead of writing authentication logic in 30 different API routes, one proxy handles it.

**4. Organization context**

Every request can carry the active organization ID.

**5. Consistent error handling**

The backend's original status code and response body are preserved.

**6. File handling**

Uploads and downloads can pass through without converting binary files into text.

This is the main purpose of the entire file.

## **2. First concept: what is a proxy?**

A proxy is an intermediary between two systems.

Suppose you want to communicate with a backend server.

Instead of sending the request directly:

```
Browser ──────────────> FastAPI
```

You send it through another server:

```
Browser ─────> Next.js ─────> FastAPI
```

The Next.js server receives the browser's request, creates a request to FastAPI, and sends the backend response back to the browser.

It acts like a middleman.

But this is not just a simple network proxy. It is an **application-level proxy**, because it also understands:

- Authentication cookies
- Bearer tokens
- Organization headers
- HTTP methods
- Request bodies
- Response status codes
- Response headers
- Compression

That is why this code is more sophisticated than simply redirecting a URL.

## **3. The imports**

```
import { NextRequest, NextResponse } from "next/server";

import { bffRefusal } from "@/lib/server-api";
```

### `NextRequest`

`NextRequest` is a Next.js class representing an incoming HTTP request.

It gives you access to:

```
request.method
request.url
request.nextUrl
request.headers
request.cookies
request.body
```

For example, if the browser sends:

```
GET /api/agents HTTP/1.1
```

Next.js creates a request object that your handler can inspect.

### `NextResponse`

`NextResponse` is used to construct the response that Next.js sends back to the browser.

For example:

```
return new NextResponse("Hello", {
  status: 200,
});
```

This produces an HTTP response with:

```
HTTP/1.1 200 OK

Hello
```

### `bffRefusal`

```
import { bffRefusal } from "@/lib/server-api";
```

This is a project-specific helper.

It creates a standardized refusal response from the Backend-for-Frontend layer.

For example:

```
bffRefusal("NOT_AUTHENTICATED", 401);
```

The exact response body depends on how `bffRefusal` is implemented, but conceptually it means:

```
Status: 401 Unauthorized

Error: NOT_AUTHENTICATED
```

## **4. Backend URL and organization header**

```
const BACKEND_URL =
  process.env.BACKEND_URL || "http://localhost:8000";
```

This is an example of an **environment variable**.

An environment variable allows you to configure your application without hardcoding deployment-specific values into your source code.

For local development:

```
BACKEND_URL=http://localhost:8000
```

For a deployed environment:

```
BACKEND_URL=https://backend.example.com
```

The code uses:

```
process.env.BACKEND_URL
```

to read the value from the server's environment.

If the variable is missing, it uses:

```
"http://localhost:8000"
```

This is called a fallback value.

### **Why is this important?**

Your code can remain the same in development, testing, and production.

You change the configuration, not the source code.

Next:

```
const ORG_HEADER = "X-Organization-Id";
```

This defines a custom HTTP header.

HTTP headers carry additional information about a request.

For example:

```
GET /api/v1/agents HTTP/1.1
Authorization: Bearer abc123
X-Organization-Id: org-456
```

The backend can interpret this as:

- The user is authenticated using token `abc123`.
- The request is intended for organization `org-456`.

The organization header is particularly important in multi-tenant applications.

A multi-tenant platform serves multiple organizations using the same application and backend infrastructure.

For example:

```
Organization A
    ├── Agents
    ├── Runs
    └── Knowledge base

Organization B
    ├── Agents
    ├── Runs
    └── Knowledge base
```

The same endpoint:

```
/api/v1/agents
```

may return different data depending on the organization.

Without the organization ID, the backend might select the wrong organization.

**Important:** The organization header identifies the requested organization. The backend must still verify that the authenticated user is allowed to access it. A header alone is not an authorization mechanism.

## **5. HTTP methods and request bodies**

```
const WITH_BODY = new Set(["POST", "PUT", "PATCH"]);
```

This introduces two concepts: HTTP methods and the JavaScript `Set` data structure.

### **What is an HTTP method?**

An HTTP method tells the server what kind of operation the client wants to perform.

| Method | Typical purpose                          |
| ------ | ---------------------------------------- |
| GET    | Retrieve information                     |
| POST   | Create something or execute an operation |
| PUT    | Replace a resource                       |
| PATCH  | Partially update a resource              |
| DELETE | Delete a resource                        |

For example:

```
GET /api/agents
```

means retrieve agents.

```
POST /api/agents
```

means create an agent.

```
PATCH /api/agents/123
```

means update some properties of agent 123.

### **What is&#x20;**`Set`**?**

A JavaScript `Set` is a collection of unique values.

```
const methods = new Set(["POST", "PUT", "PATCH"]);
```

You can check whether a value exists using:

```
methods.has("POST");
```

Result:

```
true
```

But:

```
methods.has("GET");
```

Result:

```
false
```

Therefore:

```
WITH_BODY.has(request.method)
```

checks whether the incoming HTTP method is one of the methods that this proxy forwards with a request body.

Why?

Because GET requests usually retrieve data and do not need a body.

POST, PUT, and PATCH commonly carry data.

For example, when creating an agent:

```
{
  "name": "Data Analyst",
  "description": "Analyzes company data"
}
```

The JSON is the request body.

## **6. Response headers: what does&#x20;**`DESCRIBES_THE_BODY`**&#x20;mean?**

```
const DESCRIBES_THE_BODY = [
  "content-type",
  "content-disposition",
  "cache-control",
  "content-length",
];
```

This array contains HTTP response headers that the proxy wants to preserve.

Let's understand each one.

### `Content-Type`

Describes the type of content in the response.

Examples:

```
Content-Type: application/json
```

The body contains JSON.

```
Content-Type: application/pdf
```

The body contains a PDF.

```
Content-Type: image/png
```

The body contains a PNG image.

If the backend returns a PDF but the proxy changes the content type to JSON, the browser may not handle the download correctly.

### `Content-Disposition`

This header often tells the browser how to handle a file.

Example:

```
Content-Disposition: attachment; filename="report.pdf"
```

It tells the browser that the response should be treated as a downloadable attachment with the suggested filename `report.pdf`.

Without preserving this header, the browser might lose the intended filename or download behavior.

### `Cache-Control`

This controls whether a response may be stored and reused by caches.

Example:

```
Cache-Control: no-store
```

means the response should not be stored.

Another example:

```
Cache-Control: public, max-age=3600
```

allows a response to be cached under the specified conditions.

This proxy has a special default policy, which we will examine shortly.

### `Content-Length`

This describes the size of the response body in bytes.

For example:

```
Content-Length: 1048576
```

means the body is 1,048,576 bytes, or approximately 1 MiB.

The browser can use this information to display download progress.

For example:

```
Downloaded: 500 KB
Total:      1 MB
Progress:   50%
```

If the response is streamed without a known length, the browser may not know the total size in advance.

## **7. The function&#x20;**`describingHeaders()`

This function is responsible for copying selected response headers from FastAPI to the browser.

```
function describingHeaders(source: Headers): Headers {
  const headers = new Headers();
```

Here:

- `source` contains the headers received from FastAPI.
- `headers` is a new collection of headers that will be sent to the browser.

The function does not copy every backend header. It copies only the headers that the proxy considers appropriate.

### **Step 1: Check whether the backend response was compressed**

```
const decoded = source.has("content-encoding");
```

The `Content-Encoding` header tells the receiver whether the body has been encoded, commonly compressed.

Example:

```
Content-Encoding: gzip
```

This means the response body was gzip-compressed.

The code stores the result in:

```
decoded
```

If the backend response contains that header, `decoded` becomes `true`.

### **Step 2: Loop through the selected headers**

```
for (const name of DESCRIBES_THE_BODY) {
```

This loops over:

```
content-type
content-disposition
cache-control
content-length
```

For each header, the code decides whether to copy it.

### **Step 3: Skip the content length when necessary**

```
if (decoded && name === "content-length") continue;
```

This is a very important detail.

Suppose FastAPI sends a compressed response:

```
Original JSON size:       1,000,000 bytes
Compressed gzip size:       200,000 bytes
```

The backend declares:

```
Content-Encoding: gzip
Content-Length: 200000
```

But the `fetch()` API normally exposes the response body after automatic decompression.

So the proxy receives the decoded body:

```
1,000,000 bytes
```

If it forwards the original:

```
Content-Length: 200000
```

the header would no longer describe the body being forwarded.

That would be incorrect.

Therefore:

```
if (decoded && name === "content-length") continue;
```

means:

> If the backend response was compressed, do not copy its original content length, because the body may now have a different size.

### **Step 4: Read and copy the header**

```
const value = source.get(name);
```

This retrieves the value of a header.

For example:

```
source.get("content-type");
```

might return:

```
application/pdf
```

Then:

```
if (value) headers.set(name, value);
```

copies that value into the new headers collection.

### **Step 5: Provide defaults**

```
if (!headers.has("content-type")) {
  headers.set("content-type", "application/json");
}
```

If the backend did not provide a content type, this code assumes JSON.

Then:

```
if (!headers.has("cache-control")) {
  headers.set("cache-control", NO_POLICY_MEANS);
}
```

If the backend did not provide a caching policy, the proxy uses its own default.

We will now examine why that default is important.

## **8. The caching problem:&#x20;**`NO_POLICY_MEANS`

```
const NO_POLICY_MEANS = "no-store";
```

This is one of the most important architectural decisions in the file.

### **What is caching?**

Caching means storing a response so that it can be reused later instead of requesting it again from the server.

Imagine your frontend requests:

```
GET /api/agents
```

The backend returns:

```
[
  {
    "id": "1",
    "name": "Data Analyst"
  }
]
```

Now suppose you create another agent.

The frontend sends:

```
POST /api/agents
```

The backend successfully creates:

```
{
  "id": "2",
  "name": "HR Analyst"
}
```

Then the frontend immediately requests:

```
GET /api/agents
```

You expect:

```
[
  {
    "id": "1",
    "name": "Data Analyst"
  },
  {
    "id": "2",
    "name": "HR Analyst"
  }
]
```

But if a cache reuses the previous response, the browser may receive:

```
[
  {
    "id": "1",
    "name": "Data Analyst"
  }
]
```

The new agent appears to be missing.

This is a stale response.

### **What does&#x20;**`no-store`**&#x20;do?**

```
Cache-Control: no-store
```

instructs caches not to store the response.

The code also uses:

```
cache: "no-store"
```

in the outgoing `fetch()` request.

These are two separate things:

| Setting                             | What it controls                                     |
| ----------------------------------- | ---------------------------------------------------- |
| `fetch(..., { cache: "no-store" })` | Next.js/server-side fetch caching behavior           |
| Response `Cache-Control: no-store`  | Whether the response should be stored by HTTP caches |

The proxy uses both because the response depends on:

- The user's authentication
- The user's permissions
- The active organization
- Data that may change after a write

For these mutable, organization-scoped API responses, caching could produce incorrect results.

**Important distinction:** `no-store` is a cache policy. It does not mean that the backend database cannot store the data. It means the HTTP response should not be stored in a cache.

## **9.&#x20;**`acceptsGzip()`**&#x20;— understanding compression negotiation**

```
function acceptsGzip(header: string | null): boolean {
  return (header ?? "").split(",").some((entry) => {
    const [coding, ...params] = entry
      .split(";")
      .map((part) => part.trim().toLowerCase());

    const quality = params.find((param) => param.startsWith("q="));

    return coding === "gzip" &&
      (quality === undefined || Number(quality.slice(2)) > 0);
  });
}
```

This function answers a specific question:

> Does the browser say it can accept a gzip-compressed response?

### **First: what is gzip?**

Gzip is a compression format.

Suppose your backend returns a JSON response:

```
{
  "description": "A very long description...",
  "data": "A very large amount of text..."
}
```

The response might be 5 MB.

After gzip compression, it might become 800 KB.

Compression can reduce the amount of data sent over the network.

### **Second: what is&#x20;**`Accept-Encoding`**?**

When a browser sends a request, it can tell the server which compression formats it supports.

For example:

```
Accept-Encoding: gzip, br
```

This means the browser accepts gzip and Brotli compression.

The server may then return:

```
Content-Encoding: gzip
```

### **Understanding the code**

```
header ?? ""
```

The `??` operator is called the nullish coalescing operator.

It means:

> If the value is `null` or `undefined`, use the value on the right.

So:

```
header ?? ""
```

means use an empty string if the header is missing.

Next:

```
.split(",")
```

splits the header into separate entries.

For example:

```
gzip, br
```

becomes:

```
["gzip", " br"]
```

Then:

```
.some(...)
```

checks whether at least one entry satisfies the condition.

### **What is the&#x20;**`q`**&#x20;parameter?**

The `q` parameter expresses a preference or quality value.

For example:

```
Accept-Encoding: gzip;q=1.0, br;q=0.8
```

Here:

- `gzip;q=1.0` means gzip is fully acceptable.
- `br;q=0.8` means Brotli is acceptable with a lower preference.

A value of zero means the client does not accept that encoding:

```
Accept-Encoding: gzip;q=0
```

The code checks:

```
Number(quality.slice(2)) > 0
```

For:

```
q=0.5
```

`slice(2)` produces:

```
0.5
```

Then:

```
Number("0.5")
```

produces:

```
0.5
```

And:

```
0.5 > 0
```

is `true`.

If the header is:

```
Accept-Encoding: gzip;q=0
```

the function returns `false`.

If gzip is listed without a `q` parameter:

```
Accept-Encoding: gzip
```

the code treats it as acceptable.

This function is intentionally simple. It specifically checks for gzip; it is not a complete implementation of every HTTP content-negotiation rule.

# **10. The main function:&#x20;**`platformProxy()`

Now we reach the heart of the code.

```
export function platformProxy(): ProxyHandlers {
```

This function creates and returns a collection of HTTP request handlers.

The return type is:

```
ProxyHandlers
```

That type was defined earlier:

```
export type ProxyHandlers = {
  GET: Handler;
  POST: Handler;
  PUT: Handler;
  PATCH: Handler;
  DELETE: Handler;
};
```

Each property must be a function that handles an incoming request.

The function returns:

```
{
  GET: forward,
  POST: forward,
  PUT: forward,
  PATCH: forward,
  DELETE: forward
}
```

Notice something very important:

**All five HTTP methods use the same function.**

Instead of implementing five separate handlers, the code defines one reusable handler called `forward`.

## **11. What is a handler?**

```
type Handler = (request: NextRequest) => Promise<Response>;
```

This is a TypeScript type definition.

Let's break it down.

### `(request: NextRequest)`

The handler receives a request object.

For example:

```
request.method
```

might be:

```
POST
```

### `Promise<Response>`

The handler returns a promise that eventually resolves to a response.

Why a promise?

Because the handler performs asynchronous operations:

```
await request.arrayBuffer()
```

and:

```
await fetch(url, ...)
```

Network communication takes time.

The function cannot necessarily produce the response immediately.

### **What does&#x20;**`async`**&#x20;mean?**

Later, the code defines:

```
const forward: Handler = async (request) => {
```

The `async` keyword allows the function to use `await`.

For example:

```
const response = await fetch(url);
```

means:

> Start the network request and wait until the response is available before continuing.

The `await` does not block the entire server. It suspends this particular asynchronous function while the network operation is in progress.

# **12. Step-by-step request forwarding**

Let's imagine the browser sends this request:

```
POST /api/agents HTTP/1.1
Content-Type: application/json
X-Organization-Id: org-123
Cookie: access_token=secret-token

{
  "name": "Data Analyst"
}
```

Now let's follow the request through the code.

### **Step 1: Read the access token**

```
const accessToken =
  request.cookies.get("access_token")?.value;
```

This is a very important security concept.

The browser sends the cookie automatically when making an eligible same-origin request.

The cookie contains:

```
access_token=secret-token
```

Next.js reads the cookie on the server.

The expression:

```
request.cookies.get("access_token")
```

returns the cookie object if it exists.

Then:

```
?.value
```

uses optional chaining.

It means:

> If the cookie exists, read its value. If it does not exist, return `undefined` instead of throwing an error.

### **Why use an HttpOnly cookie?**

An `HttpOnly` cookie cannot be accessed using JavaScript such as:

```
document.cookie
```

This helps prevent client-side JavaScript from directly reading the access token.

The browser can still send the cookie to the server.

So the architecture is:

```
Browser
  |
  | Cookie automatically included
  v
Next.js server
  |
  | Reads access token
  v
FastAPI
```

The token does not need to be exposed to React code.

### **Step 2: Check authentication**

```
if (!accessToken) {
  return bffRefusal("NOT_AUTHENTICATED", 401);
}
```

If the token is missing, the proxy refuses to forward the request.

The status code:

```
401 Unauthorized
```

means the request does not have valid authentication credentials.

The backend is not contacted in this case.

This is called an early return.

An early return exits the function immediately.

## **13. Constructing the backend URL**

```
const path = request.nextUrl.pathname.replace(/^\/api/, "");
```

Suppose the browser requested:

```
/api/agents
```

Then:

```
request.nextUrl.pathname
```

returns:

```
/api/agents
```

Now examine:

```
replace(/^\/api/, "")
```

This is a regular expression.

The pattern:

```
^\/api
```

means:

- `^` = beginning of the string
- `\/` = a literal forward slash
- `api` = the letters `api`

So it matches `/api` at the beginning of the path.

The replacement:

```
""
```

removes that prefix.

Result:

```
/agents
```

This is the path that will be appended to the backend's API version.

Next:

```
const url =
  `${BACKEND_URL}/api/v1${path}${request.nextUrl.search}`;
```

This is a template literal.

The backticks allow JavaScript expressions to be inserted using:

```
${...}
```

Suppose:

```
BACKEND_URL = "http://localhost:8000"
```

and:

```
path = "/agents"
```

and the browser requested:

```
/api/agents?limit=10
```

Then:

```
request.nextUrl.search
```

returns:

```
?limit=10
```

The final URL becomes:

```
http://localhost:8000/api/v1/agents?limit=10
```

The proxy has translated the frontend path into the backend path.

### **Why preserve the query string?**

Query parameters often contain filtering, pagination, and search information.

Examples:

```
/api/agents?page=2
```

```
/api/runs?status=completed
```

```
/api/skills?search=python
```

If the proxy dropped the query string, the backend would receive a different request.

## **14. Forwarding the organization ID**

```
const organizationId =
  request.headers.get(ORG_HEADER);
```

This reads:

```
X-Organization-Id: org-123
```

from the incoming request.

Then the code prepares the outgoing headers:

```
headers: {
  Authorization: `Bearer ${accessToken}`,
  ...(contentType ? { "Content-Type": contentType } : {}),
  ...(organizationId ? { [ORG_HEADER]: organizationId } : {}),
},
```

This is one of the most important parts of the proxy.

### **What is a Bearer token?**

The backend receives authentication through:

```
Authorization: Bearer secret-token
```

The word `Bearer` is part of the standard authorization format.

It tells the backend that the following value is a bearer access token.

FastAPI can then validate the token and determine the authenticated user.

### **Why not forward the cookie directly?**

The backend is receiving a server-to-server request from Next.js.

The proxy extracts the token from the browser cookie and converts it into the authorization header expected by FastAPI.

The browser does not need to know how the backend authenticates requests.

### **What is the&#x20;**`...`**&#x20;operator here?**

This is the JavaScript object spread syntax.

For example:

```
const headers = {
  Authorization: "Bearer token",
  ...(true ? { "Content-Type": "application/json" } : {}),
};
```

The result is:

```
{
  Authorization: "Bearer token",
  "Content-Type": "application/json"
}
```

If the condition is false:

```
...(false ? { "Content-Type": "application/json" } : {})
```

the empty object is spread instead.

Nothing is added.

### **Why use&#x20;**`[ORG_HEADER]`**?**

```
{ [ORG_HEADER]: organizationId }
```

This is called a computed property name.

Because:

```
ORG_HEADER = "X-Organization-Id"
```

the object becomes:

```
{
  "X-Organization-Id": "org-123"
}
```

The square brackets tell JavaScript to use the value of the variable as the property name.

Without the square brackets:

```
{ ORG_HEADER: organizationId }
```

the object would contain a property literally named:

```
ORG_HEADER
```

That would be incorrect.

# **15. Why&#x20;**`Content-Type`**&#x20;is forwarded dynamically**

The code reads:

```
const contentType =
  request.headers.get("content-type");
```

Then it forwards it:

```
...(contentType ? { "Content-Type": contentType } : {}),
```

Why not always set:

```
Content-Type: application/json
```

Because not every request contains JSON.

Consider two cases.

### **Case A: JSON request**

The browser sends:

```
Content-Type: application/json
```

with a body:

```
{
  "name": "Data Analyst"
}
```

The proxy forwards the same content type.

FastAPI knows how to parse the JSON body.

### **Case B: File upload**

The browser sends a file using `multipart/form-data`.

The content type might be:

```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryABC123
```

The `boundary` is important.

It separates the different parts of the multipart body.

If the proxy changes the content type to:

```
Content-Type: application/json
```

FastAPI will try to interpret the body as JSON, even though it contains multipart data.

The upload will fail.

That is why the proxy preserves the original content type.

# **16. The request body: why use&#x20;**`arrayBuffer()`**?**

This is a particularly important concept.

```
body: WITH_BODY.has(request.method)
  ? await request.arrayBuffer()
  : undefined,
```

Let's understand what this does.

### **What is a request body?**

A request body is the data sent with an HTTP request.

For example:

```
POST /api/agents
Content-Type: application/json

{
  "name": "Data Analyst"
}
```

The JSON is the body.

But a body is not always text.

It can contain:

- JSON
- Plain text
- Images
- PDFs
- Audio
- Video
- Multipart file uploads
- Other binary data

### **What is binary data?**

Binary data is raw bytes.

A byte is a unit of data containing 8 bits.

For example, a PDF file is not fundamentally a string of text. It is a sequence of bytes that follows the PDF file format.

If you read it as text, you may lose or alter information.

### **What is&#x20;**`ArrayBuffer`**?**

An `ArrayBuffer` is a JavaScript object representing a fixed-length region of binary data.

For example:

```
const data = await request.arrayBuffer();
```

This reads the request body into an `ArrayBuffer`.

It does not attempt to interpret the body as JSON or as a string.

That is important because the proxy wants to forward the body without changing its content.

### **Why not&#x20;**`request.text()`**?**

Suppose the user uploads:

```
report.pdf
```

The PDF contains binary bytes.

If you do:

```
const body = await request.text();
```

JavaScript tries to decode those bytes into text.

Some byte sequences may not correspond to valid text characters.

The conversion can change the representation of the file.

If you then send that text to FastAPI, the resulting bytes may no longer match the original PDF.

Therefore:

```
await request.arrayBuffer()
```

is more appropriate for a generic proxy that supports both text and binary requests.

### **Why not&#x20;**`request.json()`**?**

Because that would require every request body to be JSON.

A generic proxy must also support:

```
multipart/form-data
application/pdf
image/png
application/octet-stream
```

Using `arrayBuffer()` keeps the proxy independent of the body format.

### **What does the ternary operator mean?**

```
condition ? valueIfTrue : valueIfFalse
```

Here:

```
WITH_BODY.has(request.method)
  ? await request.arrayBuffer()
  : undefined
```

means:

- If the method is POST, PUT, or PATCH, read the request body.
- Otherwise, do not provide a body.

The resulting `fetch()` call forwards the body to FastAPI.

## **17. Why the request is buffered instead of streamed**

The code comment says:

> The request is not streamed because a streamed request body cannot be replayed.

This is a subtle but important networking concept.

### **What is streaming?**

Streaming means processing or transferring data progressively rather than waiting for the entire data set to be available.

For example, imagine uploading a 100 MB file.

With streaming:

```
Read first chunk  ──> Send first chunk
Read second chunk ──> Send second chunk
Read third chunk  ──> Send third chunk
...
```

The proxy does not need to hold the entire file in memory before sending it.

With buffering:

```
Read entire file
       |
       v
Store in memory
       |
       v
Send entire body
```

The code uses buffering for the request:

```
await request.arrayBuffer()
```

### **Why does buffering matter for redirects?**

FastAPI may return a redirect if a request uses a URL with a trailing-slash mismatch.

For example:

```
/api/v1/agents
```

might redirect to:

```
/api/v1/agents/
```

A redirect with status:

```
307 Temporary Redirect
```

preserves the original HTTP method and request body.

The client must therefore resend the body to the new URL.

A buffered body can be replayed.

A streaming body may already have been consumed and cannot necessarily be sent again.

That is the reason this code buffers the request.

### **Why is&#x20;**`Content-Length`**&#x20;important for uploads?**

The code comment also mentions:

```
BodySizeLimitMiddleware
```

This is a backend middleware that apparently uses the `Content-Length` header to reject oversized uploads early.

For example:

```
Content-Length: 104857600
```

indicates a body of approximately 100 MiB.

The middleware can compare the declared size against an upload limit before accepting the entire body.

The proxy's buffering strategy and request headers therefore interact with the backend's upload protection.

**Trade-off:** Buffering makes replay easier but can use significant memory for large uploads. This implementation deliberately chooses replayability and compatibility over streaming the request body.

# **18. The outgoing&#x20;**`fetch()`**&#x20;request**

Now we can understand the entire outgoing request:

```
const response = await fetch(url, {
  method: request.method,

  headers: {
    Authorization: `Bearer ${accessToken}`,
    ...(contentType ? { "Content-Type": contentType } : {}),
    ...(organizationId ? { [ORG_HEADER]: organizationId } : {}),
  },

  body: WITH_BODY.has(request.method)
    ? await request.arrayBuffer()
    : undefined,

  cache: "no-store",
});
```

This is where Next.js actually contacts FastAPI.

Let's map the original request to the backend request.

## **Request transformation**

Browser request

POST /api/agents

Cookie: access_token=...

X-Organization-Id: org-123

Body: JSON

Next.js proxy

Reads cookie and prepares request

Cookie → Authorization: Bearer token

Preserves organization and content type

Preserves body bytes

FastAPI request

POST /api/v1/agents

Authorization: Bearer ...

X-Organization-Id: org-123

Body: same JSON bytes

The key point is that the proxy changes the URL and authentication mechanism, but preserves the request's important meaning.

## **19. The backend response: why return it directly?**

After the backend responds:

```
const response = await fetch(url, ...);
```

the variable `response` is a standard Fetch API `Response`.

It contains:

```
response.status
response.headers
response.body
```

For example, FastAPI might return:

```
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "detail": "You do not have permission to perform this action"
}
```

The proxy should not turn this into:

```
HTTP/1.1 500 Internal Server Error
```

That would misrepresent what happened.

The backend knows why the request failed.

The proxy should preserve the backend's status and body.

This is what the following code does.

# **20. The response body is streamed**

```
const headers = describingHeaders(response.headers);

let body = response.body;
```

Notice that the response body is not read using:

```
await response.text()
```

or:

```
await response.arrayBuffer()
```

Instead, it takes:

```
response.body
```

which is a `ReadableStream`.

### **What is a&#x20;**`ReadableStream`**?**

A `ReadableStream` allows data to be read progressively.

Imagine downloading a 500 MB file.

Without streaming:

```
Wait for 500 MB
       |
       v
Receive complete file
       |
       v
Start sending to browser
```

With streaming:

```
Backend sends chunk 1
       |
       v
Browser receives chunk 1

Backend sends chunk 2
       |
       v
Browser receives chunk 2

...
```

The browser can start receiving the file before the backend has finished sending it.

This reduces the time to the first byte and avoids buffering the entire response in the proxy.

### **Why is this useful?**

For your AI platform, consider:

- Downloading reports
- Exporting datasets
- Downloading PDFs
- Receiving large agent outputs
- Returning large knowledge-base documents

Streaming can make these operations more efficient.

The proxy is buffering the incoming request but streaming the outgoing response.

That is a deliberate asymmetry.

## **21. What happens with a 204 response?**

The code comment says:

```
// a 204 carries a null body and stays empty
```

A `204 No Content` response means the operation succeeded but there is no response body.

For example, a DELETE operation might return:

```
HTTP/1.1 204 No Content
```

There is no JSON object to return.

The code:

```
let body = response.body;
```

will receive a null body for such a response.

Then the proxy passes that body to `NextResponse`.

This preserves the empty response instead of inventing a JSON body.

## **22. The compression problem: why compress again?**

This is probably the most technically interesting part of the code.

```
if (body && response.headers.has("content-encoding")) {
  headers.set("vary", "Accept-Encoding");

  if (acceptsGzip(request.headers.get("accept-encoding"))) {
    body = body.pipeThrough(new CompressionStream("gzip"));
    headers.set("content-encoding", "gzip");
  }
}
```

Let's understand the complete situation.

### **Step 1: FastAPI sends a compressed response**

Suppose the backend returns:

```
Content-Encoding: gzip
Content-Length: 200000
```

The backend has compressed the response.

### **Step 2: Next.js&#x20;**`fetch()`**&#x20;automatically decompresses it**

The Fetch API generally handles supported content encodings automatically.

So the body that Next.js receives may already be decoded.

For example:

```
Backend sends:     200 KB gzip data
Next.js receives:  1 MB decoded data
```

The proxy now has a problem.

It wants to forward the response to the browser.

But the backend's original compression has already been removed by `fetch()`.

### **Step 3: Check whether the browser accepts gzip**

```
acceptsGzip(request.headers.get("accept-encoding"))
```

If the browser accepts gzip, the proxy can compress the body again.

### **Step 4: Compress the stream**

```
body = body.pipeThrough(
  new CompressionStream("gzip")
);
```

This is a stream transformation.

`pipeThrough()` connects one stream to another transformation stream.

Conceptually:

```
Readable stream
      |
      v
Gzip compression
      |
      v
Compressed readable stream
```

The original response body is transformed into gzip-compressed data.

### **Step 5: Tell the browser the response is compressed**

```
headers.set("content-encoding", "gzip");
```

This header is essential.

Without it, the browser would interpret the compressed bytes as ordinary response content.

The browser needs to know:

```
Content-Encoding: gzip
```

so that it can decode the response.

### **Why set&#x20;**`Vary`**?**

```
headers.set("vary", "Accept-Encoding");
```

This header tells caches that the response representation depends on the request's `Accept-Encoding` header.

For example:

```
Browser A accepts gzip
Browser B does not accept gzip
```

The response may be compressed for Browser A and uncompressed for Browser B.

A cache must not confuse these two representations.

`Vary: Accept-Encoding` helps prevent that.

However, this particular proxy also uses `Cache-Control: no-store` by default, so ordinary caching of these API responses is discouraged.

## **23. The final response**

```
return new NextResponse(body, {
  status: response.status,
  headers,
});
```

This constructs the response that the browser receives.

It preserves:

```
response.status
```

the backend's HTTP status code.

It also preserves the selected response headers:

```
headers
```

And it forwards:

```
body
```

the backend response stream, possibly compressed again.

The complete response path is:

```
FastAPI
   |
   | HTTP status
   | Response headers
   | Response body stream
   v
Next.js proxy
   |
   | Preserve status
   | Preserve selected headers
   | Preserve body
   v
Browser
```

The proxy does not need to understand every business response.

It only needs to forward the response correctly.

## **24. Why one function handles all five methods**

At the end:

```
return {
  GET: forward,
  POST: forward,
  PUT: forward,
  PATCH: forward,
  DELETE: forward,
};
```

This is a simple object.

Each property points to the same function.

For example:

```
GET: forward
```

means the GET handler is the `forward` function.

It does not execute the function immediately.

It assigns the function as a value.

### **Why is this useful?**

Suppose you have 30 backend endpoints.

Without a shared proxy, you might have 30 Next.js route files with repeated code:

```
const token = ...
const response = await fetch(...)
return ...
```

One developer might forget:

```
X-Organization-Id
```

Another might forget:

```
cache: "no-store"
```

Another might convert a PDF response to text.

The shared proxy reduces these inconsistencies.

A new backend endpoint can often be accessed through the existing catch-all proxy without creating another frontend forwarding route.

That is the meaning of the comment:

> A new backend route needs no frontend change at all.

It is not necessarily saying that the frontend needs no change to build a new UI feature. It means the forwarding infrastructure does not need another route implementation for every backend endpoint.

# **25. How is this function actually used by Next.js?**

One final concept: defining a function does not automatically create an API endpoint.

Next.js needs a route file that exports the handlers.

For example, a catch-all API route could look like this:

```
// app/api/[...path]/route.ts

import { platformProxy } from "@/lib/platform-proxy";

const handlers = platformProxy();

export const GET = handlers.GET;
export const POST = handlers.POST;
export const PUT = handlers.PUT;
export const PATCH = handlers.PATCH;
export const DELETE = handlers.DELETE;
```

This is an illustrative example of how the function could be mounted.

The exact route file in your project may be different.

The important concept is that Next.js expects named exports such as:

```
export const GET = ...
```

When a browser requests:

```
/api/agents
```

Next.js finds the matching route and invokes its GET handler.

That handler calls the shared `forward` function.

The function then forwards the request to FastAPI.

# **26. The complete architecture in one example**

Let's walk through a real scenario in your AI platform.

Suppose a user is working inside an organization called:

```
Organization: Acme AI
Organization ID: org-123
```

The user creates a new AI agent.

## **Step 1: Browser sends the request**

```
POST /api/agents
Content-Type: application/json
X-Organization-Id: org-123
Cookie: access_token=abc123

{
  "name": "Business Analyst",
  "description": "Analyzes business data"
}
```

## **Step 2: Next.js proxy receives it**

The proxy:

1. Reads the access token from the cookie.
2. Checks that the token exists.
3. Extracts `/agents` from `/api/agents`.
4. Preserves the query string if one exists.
5. Reads the organization ID.
6. Preserves the content type.
7. Reads the body as bytes.
8. Creates a backend request.

## **Step 3: FastAPI receives the request**

```
POST /api/v1/agents
Authorization: Bearer abc123
X-Organization-Id: org-123
Content-Type: application/json

{
  "name": "Business Analyst",
  "description": "Analyzes business data"
}
```

FastAPI can now:

- Authenticate the user.
- Check organization membership.
- Check the user's permissions.
- Validate the request.
- Create the agent in the database.

## **Step 4: FastAPI returns the result**

```
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "agent-456",
  "name": "Business Analyst"
}
```

## **Step 5: Next.js forwards the response**

The proxy preserves the backend's status code:

```
201 Created
```

and its response body.

The browser receives the response and can update the UI.

# **27. Important concepts to remember**

**Authentication**

The proxy reads the access token from an HttpOnly cookie and sends it to FastAPI using the Bearer authorization header.

**Multi-tenancy**

The active organization ID is forwarded so the backend can resolve the correct organization's data.

**Request forwarding**

The proxy changes the frontend API path into the backend API path and forwards the HTTP method, headers, and body.

**Binary data**

ArrayBuffer preserves request bytes. A ReadableStream allows response data to be forwarded progressively.

**Cache control**

The proxy avoids reusing potentially stale or organization-specific API responses.

## **28. One security detail you should understand**

This proxy is a security boundary, but it does not replace backend authorization.

For example, a malicious client might send:

```
X-Organization-Id: org-999
```

even if the user normally works in:

```
org-123
```

The proxy forwards the organization ID. It does not independently prove that the user belongs to that organization.

Therefore, FastAPI must validate:

```
Authenticated user
        |
        v
Is the user a member of org-999?
        |
        v
Does the user have permission for this operation?
        |
        v
Allow or reject
```

The backend must never trust the organization ID merely because it came through the Next.js proxy.

Also, because the proxy forwards only selected headers, headers such as `Cookie`, `Accept`, and arbitrary custom headers are not automatically forwarded. That is intentional in many designs, but if a future backend endpoint requires another header, the proxy may need to be updated.

## **Final mental model**

Think of `platformProxy()` as a **central gateway between your frontend and backend**.

It performs four main jobs:

- **Authenticate:** Read the token from the secure cookie.
- **Prepare:** Construct the backend URL and attach the organization context.
- **Forward:** Send the request while preserving its method, content type, and body bytes.
- **Return:** Pass the backend's status, selected headers, and response stream back to the browser.

The most important architectural idea is this:

**Your frontend should not need to know how to authenticate with FastAPI, how the backend URL is configured, or how every individual endpoint is forwarded. The shared proxy handles those concerns in one place.**

That makes the platform easier to maintain as you add more AI capabilities, agents, analytics, HR tools, knowledge-base features, and organization-scoped APIs.