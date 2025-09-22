from supabase import create_client, Client
from app.core.config import settings
from typing import Optional

class SupabaseManager:
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.anon_key = settings.SUPABASE_ANON_KEY
        self.service_role_key = settings.SUPABASE_SERVICE_ROLE_KEY
        self._client: Optional[Client] = None
        self._service_client: Optional[Client] = None

    @property
    def client(self) -> Client:
        """Get Supabase client with anon key"""
        if self._client is None:
            self._client = create_client(self.url, self.anon_key)
        return self._client

    @property
    def service_client(self) -> Client:
        """Get Supabase client with service role key for admin operations"""
        if self._service_client is None:
            self._service_client = create_client(self.url, self.service_role_key)
        return self._service_client

    def get_user_client(self, access_token: str) -> Client:
        """Get Supabase client with user's access token"""
        client = create_client(self.url, self.anon_key)
        client.auth.set_session(access_token, "")
        return client

supabase_manager = SupabaseManager()