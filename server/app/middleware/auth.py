from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import jwt_handler
import re

class AuthMiddleware(BaseHTTPMiddleware):
    # Routes that don't require authentication
    PUBLIC_ROUTES = [
        r"^/$",
        r"^/docs.*",
        r"^/redoc.*",
        r"^/openapi\.json$",
        r"^/health$",
        # Add any other public routes here
    ]

    def __init__(self, app):
        super().__init__(app)

    def is_public_route(self, path: str) -> bool:
        """Check if the route is public (doesn't require authentication)"""
        return any(re.match(pattern, path) for pattern in self.PUBLIC_ROUTES)

    async def dispatch(self, request: Request, call_next):
        # Skip auth for public routes
        if self.is_public_route(request.url.path):
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid authorization header"}
            )

        token = auth_header.replace("Bearer ", "")
        
        try:
            # Verify token and extract user data
            user_data = jwt_handler.verify_supabase_token(token)
            
            # Add user data to request state
            request.state.user = user_data
            request.state.user_id = user_data["user_id"]
            request.state.user_role = jwt_handler.extract_user_role(user_data)
            request.state.access_token = token
            
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Authentication processing error"}
            )

        return await call_next(request)