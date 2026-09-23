<<<<<<< HEAD
# Lab Activity: The Authentication Gauntlet

Welcome to the Auth Gauntlet! In this 30-45-minute lab, your team will explore four different mechanisms for securing web applications. By the end, you will understand the difference between **stateful** (server-memory) and **stateless** (token-based) authentication.

> **AuthN vs. AuthZ:** Every phase in this lab is about proving your identity — that's **Authentication (AuthN)**. Whether you can access a specific resource *after* proving who you are is **Authorization (AuthZ)** — a separate concern covered in the next session.

---

## Team Setup

This activity is completed in **teams of 5**. Before starting, assign the following roles. Roles rotate with each phase so everyone gets hands-on time:

| Role | Responsibility |
|---|---|
| **Driver** | Writes code and types commands — the only person at the keyboard |
| **Navigator** | Reads the instructions aloud and guides the Driver step by step |
| **REST Client Operator** | Owns the `.http` file and runs REST Client requests |
| **Postman Operator** | Owns Postman and runs the GUI verification requests |
| **Reporter** | Records answers to challenge questions and leads the wrap-up discussion |

> **Rotation rule:** After each phase, everyone shifts one role to the right. By Phase 4 most team members will have held at least two roles.

---

## Tools Primer: REST Client vs. Postman

In this lab you will test every request **twice** — first with the **VS Code REST Client extension**, then with **Postman**. This is intentional.

Most developers reach for GUI tools without understanding what an HTTP request actually looks like at the wire level. REST Client forces you to write raw HTTP syntax. Postman then shows you the same request through a visual interface. Seeing both side-by-side is how you build real fluency.

**Rule for this lab:**
1. The REST Client Operator sends the request first using the `.http` file.
2. The Postman Operator then reproduces the same request in Postman to verify.
3. Both operators confirm the responses match before the team moves on.

### Installing REST Client

1. Open VS Code → Extensions (`Ctrl+Shift+X` / `Cmd+Shift+X`).
2. Search for **REST Client** by Huachao Mao and install it.
3. Open `auth_lab.http` at the root of the project. All REST Client requests in this lab go into that file.

---

## Initial Setup (3 Minutes)

1. Clone this repository to your local machine.
2. Create and activate a virtual environment, then install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate    # macOS / Linux
   # .venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```
3. Start your server: `python manage.py runserver`.

> **Note:** Do not run migrations or create a superuser. A database with the user `admin` and password `admin123` is already included.

---

## Phase 1: Basic Authentication (7 Minutes)

Basic Auth is the simplest method — it passes credentials directly in the header of every request.

### Driver Task

Open `views.py` and locate `basic_auth_view`. **Replace the entire function** (keep the decorators) with the following:

```python
@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def basic_auth_view(request):
    # TODO: Extract and print the header
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    print(f"Incoming Header: {auth_header}")
    return Response({"message": "Check your terminal!"})
```

### REST Client Operator Task

Add the following block to `auth_lab.http` and click **Send Request**:

```http
### Phase 1 — Basic Auth (unauthenticated)
GET http://127.0.0.1:8000/api/basic/ HTTP/1.1

###

### Phase 1 — Basic Auth (with credentials)
# REST Client encodes username:password in Base64 automatically
GET http://127.0.0.1:8000/api/basic/ HTTP/1.1
Authorization: Basic YWRtaW46YWRtaW4xMjM=
```

> `YWRtaW46YWRtaW4xMjM=` is the Base64 encoding of `admin:admin123`.
> Notice you are writing the raw `Authorization` header by hand — this is exactly what Postman constructs for you behind the scenes.

### Postman Operator Task

Send a `GET` request to `http://127.0.0.1:8000/api/basic/`. In the **Authorization** tab, select **Basic Auth** and enter `admin` / `admin123`. Confirm the response matches the REST Client result.

### ⚡ Team Challenge

The Driver should check the terminal after the authenticated REST Client request.

1. You will see a string like `Basic YWRtaW46YWRtaW4xMjM=`. The Navigator pastes the Base64 part (after the word `Basic`) into [base64decode.org](https://base64decode.org). *What is the exact format of the decoded string? The Reporter writes the answer as a comment in `views.py`.*
2. Both requests were sent over **HTTP**, not **HTTPS**. Given what was covered in today's session about TLS, what does this mean about the security of those credentials — even though they don't appear as plaintext? *The Reporter writes a one-sentence answer as a comment in `views.py`.*

### Synthesis Challenge

An attacker intercepts the `Basic YWRtaW46YWRtaW4xMjM=` string off the network. They don't need to decode it. As a team, construct the **exact raw HTTP header line** the attacker would add to their own REST Client `.http` file to impersonate the admin user on the next request — without ever knowing the original password.

Add your answer as a new block in `auth_lab.http` with a comment explaining why this works. *What does this tell you about the relationship between Base64 encoding and security?*

---

## Phase 2: Session Authentication (5 Minutes)

> **Role rotation:** shift one position to the right before starting.

Session Auth is **stateful** — the server stores a session record in its own database and gives your browser a cookie as a pointer to that record.

### Browser Task (whole team observes)

1. Open a browser and go to `http://127.0.0.1:8000/admin/`.
2. Log in with `admin` / `admin123`.
3. Open Developer Tools (`F12`). Go to **Application** (Chrome) or **Storage** (Firefox) → **Cookies**.

> Note: REST Client and Postman do not handle browser cookies natively, so this phase uses the browser directly. That's an important constraint to know — session-based APIs are awkward to test without a browser or a dedicated cookie jar.

### ⚡ Team Challenge

1. Locate the cookie named `sessionid`.
2. Right-click it and select **Delete**. Refresh the page.
3. *What happens, and why? Your answer must reference both the cookie **and** the server-side session database. The Reporter adds a comment in `views.py` under `session_auth_view`.*

### Synthesis Challenge

Before deleting the cookie, the Navigator copies the full `sessionid` value and saves it somewhere. After deletion logs you out, manually re-add the cookie using DevTools:

- Chrome: **Application → Cookies → right-click the domain → Add cookie**. Set the name to `sessionid` and paste back the original value.
- Firefox: **Storage → Cookies → click the `+` icon**. Do the same.

Refresh the page. *What happens? What does this tell you about what an attacker would need to hijack an active session — and why is this called session hijacking? The Reporter writes the answer as a comment in `views.py`.*

---

## Phase 3: Token Authentication — Opaque Tokens (7 Minutes)

> **Role rotation:** shift one position to the right before starting.

An **Opaque Token** is a random string with no intrinsic meaning. The server stores it in its own database, and every incoming request triggers a database lookup to validate it.

> Keep this definition in mind — Phase 4 introduces a token that needs no database lookup at all.

### Driver Task

Stop your server (`Ctrl+C`), generate a token, then restart:

```bash
python manage.py drf_create_token admin
python manage.py runserver
```

Copy the token string from your terminal output.

### REST Client Operator Task

Add this block to `auth_lab.http`, replacing `<YOUR_TOKEN>` with the copied token:

```http
### Phase 3 — Opaque Token Auth
GET http://127.0.0.1:8000/api/token/ HTTP/1.1
Authorization: Token <YOUR_TOKEN>
```

Send the request and confirm a 200 response.

Now tamper with the token by changing its last character and send again:

```http
### Phase 3 — Tampered Token
GET http://127.0.0.1:8000/api/token/ HTTP/1.1
Authorization: Token <YOUR_TOKEN_WITH_LAST_CHAR_CHANGED>
```

### Postman Operator Task

Reproduce the valid token request in Postman: set Authorization to **No Auth**, go to **Headers**, and add:
- **Key:** `Authorization`
- **Value:** `Token <YOUR_TOKEN>`

Confirm the response matches the REST Client result.

### ⚡ Team Challenge 1

*What HTTP status code did the tampered token return? The Reporter notes it.*

### ⚡ Team Challenge 2

The Driver runs this command to inspect password storage:

```bash
python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.get(username='admin').password)"
```

*What algorithm prefix appears at the start of the output? Why is `admin123` not stored as-is? The Reporter writes the answer as a comment in `views.py`.*

### Synthesis Challenge

Discuss as a team: your opaque token is valid indefinitely unless someone explicitly deletes it from the database.

1. *What would an attacker need to do to permanently invalidate a stolen opaque token — and who has to take that action?*
2. *Is the same true for a JWT? What is the fundamental difference in how you would revoke each type?*

The Reporter writes a two-sentence comparison as a comment in `views.py`. You don't need to implement anything — reason through it from what you know about where each token lives.

---

## Phase 4: JSON Web Tokens — JWT (8 Minutes)

> **Role rotation:** shift one position to the right before starting.

A **JWT** is **stateless** and **self-contained** — it carries user data directly inside it, cryptographically signed. The server validates it using its secret key, with no database lookup required.

### REST Client Operator Task

Add the following to `auth_lab.http`:

```http
### Phase 4 — JWT Login (obtain tokens)
POST http://127.0.0.1:8000/api/jwt/login/ HTTP/1.1
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123"
}
```

Send the request. You will receive an `access` token and a `refresh` token in the response. Copy the `access` token.

Now use it to hit a protected endpoint:

```http
### Phase 4 — JWT Protected Request
# Paste your access token below, replacing <ACCESS_TOKEN>
GET http://127.0.0.1:8000/api/jwt/protected/ HTTP/1.1
Authorization: Bearer <ACCESS_TOKEN>
```

### Postman Operator Task

Reproduce the login `POST` in Postman using **Body → raw → JSON**. Confirm the tokens match the REST Client response.

### ⚡ Team Challenge

1. Copy the `access` token. Go to [jwt.io](https://jwt.io) and paste it into the **Encoded** box.
2. Look at the purple **Payload** section. *Find the `exp` timestamp. What other piece of identifying user data is baked into the payload? The Reporter notes it as a comment in `views.py`.*
3. Reflect: Unlike Phase 3, this token was never stored in the database. *How does the server validate it without a lookup? (Hint: examine the third segment of the JWT — the Signature.) The Reporter writes a one-sentence answer as a comment.*

### Synthesis Challenge

Still on jwt.io, find the `user_id` field in the **Payload** section. Change it to `2`. Notice that jwt.io immediately regenerates an **Encoded** token on the left reflecting your edit.

Copy that tampered encoded token. Add a new block to `auth_lab.http`:

```http
### Phase 4 — Tampered JWT
GET http://127.0.0.1:8000/api/jwt/protected/ HTTP/1.1
Authorization: Bearer <PASTE_TAMPERED_TOKEN_HERE>
```

Send it. *What HTTP status code comes back? Why does the server reject it even though the token is structurally valid JSON? The Reporter writes a two-sentence explanation as a comment in `views.py` — your answer must use the word "signature".*

---

## Wrap-Up Comparison (Reporter leads)

Before you finish, the Reporter fills in this table as a comment block at the top of `views.py`. The whole team should discuss each cell:

```
# +-------------------+------------+-----------+-------------------+----------+
# | Method            | Stateful?  | DB Lookup?| Credentials sent  | Safe on  |
# |                   |            |           | every request?    | HTTP?    |
# +-------------------+------------+-----------+-------------------+----------+
# | Basic Auth        |            |           |                   |          |
# | Session Auth      |            |           |                   |          |
# | Opaque Token Auth |            |           |                   |          |
# | JWT               |            |           |                   |          |
# +-------------------+------------+-----------+-------------------+----------+
```

**Discussion prompts for the team:**
- In which phase did writing the raw HTTP header in REST Client change your understanding of what Postman was doing automatically?
- Which method would you choose for a mobile app that needs to work offline? Why?
- Which method is safest over a network you don't control?

---

*Good luck — and remember: if your transport layer is unencrypted, your entire authentication architecture is a complete illusion.*
=======
# advanced-python-programming-gla-auth-gauntlet-group-7
>>>>>>> 17834bd (Initial commit)
