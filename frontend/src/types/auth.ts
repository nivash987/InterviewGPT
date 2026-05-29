export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthUser {
  id: string;
  email: string;
  full_name: string | null;
  is_email_verified: boolean;
  roles: string[];
}

export interface RegisterResponse {
  user: AuthUser;
  tokens: TokenPair | null;
  verification_token?: string | null;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name: string | null;
  is_email_verified: boolean;
  is_active: boolean;
  roles: string[];
  permissions: string[];
  last_login_at: string | null;
  created_at: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  full_name?: string;
}
