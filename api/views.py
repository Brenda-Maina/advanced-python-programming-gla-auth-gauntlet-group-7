# ─────────────────────────────────────────────────────────────────────────────
# api/views.py — Authentication Gauntlet Lab
#
# Wrap-Up Comparison Table (Reporter fills this in at the end of the lab):
#
# +-------------------+------------+-----------+-------------------+----------+
# | Method            | Stateful?  | DB Lookup?| Credentials sent  | Safe on  |
# |                   |            |           | every request?    | HTTP?    |
# +-------------------+------------+-----------+-------------------+----------+
# | Basic Auth        |  No        | Yes       |      Yes          |   No     |
# | Session Auth      |   Yes      | Yes       |      No           |   No     |
# | Opaque Token Auth |   No       | Yes       |      No           |   No     |
# | JWT               |     No     | No        |      Yes          |   No     |
# +-------------------+------------+-----------+-------------------+----------+
#
# ─────────────────────────────────────────────────────────────────────────────

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1 — Basic Authentication
# ─────────────────────────────────────────────────────────────────────────────

@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def basic_auth_view(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    print(f"Incoming Header: {auth_header}")
    return Response({"message": "Check your terminal!"})

    # ── Driver Task ───────────────────────────────────────────────────────────
    # TODO: Extract the raw Authorization header from request.META and print
    #       it to the terminal with a descriptive label.
    #       Then return: Response({"message": "Check your terminal!"})
    #
    # Hint: the header key in request.META is 'HTTP_AUTHORIZATION'.
    # ─────────────────────────────────────────────────────────────────────────

    # Reporter — Phase 1 challenge answers:
    # Q1 answer (header format): The decoded Base64 string is "admin:admin123" the exact format is username:password.
    # Q2 answer (security over HTTP): Even though the credentials are Base64-encoded, they are NOT encrypted any attacker who intercepts the HTTP traffic can trivially decode the Base64 string and recover the plaintext username and password, because Base64 is an encoding scheme, not encryption.

    return Response({"message": "Phase 1 stub — Driver: complete the TODO above."})


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2 — Session Authentication
# ─────────────────────────────────────────────────────────────────────────────

@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def session_auth_view(request):
    # Reporter — Phase 2 challenge answers:
    # Q1 answer: Deleting the sessionid cookie logs you out immediately. The browser no longer has the pointer to the server-side session record, so Django cannot look up the session in its database and treats the request as unauthenticated.
    # Synthesis answer (session hijacking): Re-adding the original sessionid cookie value restores the authenticated session the page loads as if you never logged out. This works because the server only checks whether the sessionid value exists and is valid in its session database; it does not verify the browser or IP. An attacker who steals a valid sessionid value (e.g. via network sniffing or XSS) can paste it into their own browser and gain full access to the victim's session this is called session hijacking.

    return Response({"message": "Session authenticated.", "user": request.user.username})


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 3 — Token Authentication (Opaque)
# ─────────────────────────────────────────────────────────────────────────────

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def token_auth_view(request):
    # Reporter — Phase 3 challenge answers:
    # Q1 answer: A tampered opaque token returns HTTP 401 Unauthorized, because the modified token string does not match any record in the authtoken_token database table.
    # Q2 answer: The password is stored with the prefix "pbkdf2_sha256" Django uses PBKDF2 with SHA-256 and a random salt. "admin123" is not stored as-is because storing plaintext passwords means a single database breach exposes every user's credentials; hashing ensures only a one-way digest is stored.
    # Synthesis answer: To permanently invalidate a stolen opaque token, an admin (or the user) must explicitly delete the token row from the database the server has to take that action. For a JWT this is fundamentally different: because the token is stateless and never stored, there is no single record to delete; revocation requires either waiting for the token to expire or maintaining a server-side denylist, which reintroduces statefulness.

    return Response({"message": "Token authenticated.", "user": request.user.username})


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 4 — JSON Web Tokens (JWT)
# ─────────────────────────────────────────────────────────────────────────────

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def jwt_protected_view(request):
    # Reporter — Phase 4 challenge answers:
    # Q1 answer: The decoded payload contains "token_type", "exp" 1790464615, "iat" 1790462815, "jti" 5e09c163e0e243988a700edcd9f96b89, and "user_id" 1 the user_id is the key piece of identifying user data baked directly into the token.
    # Q2 answer: The tampered JWT returns HTTP 401 Unauthorized. Even though the payload is structurally valid JSON, the server rejects it because the signature no longer matches, the signature is computed over the original header and payload using the server's SECRET_KEY, so any change to the payload produces a signature mismatch that Django's JWTAuthentication detects immediately.
    # Synthesis answer: Because JWTs are stateless, a stolen access token cannot be invalidated before its expiry without a server-side denylist (reintroducing statefulness). The standard mitigation is to keep access token lifetimes very short (e.g. 5–15 minutes, as configured in SIMPLE_JWT) and use the refresh token which can be stored and revoked in the database to issue new access tokens.

    return Response({"message": "JWT authenticated.", "user": request.user.username})
