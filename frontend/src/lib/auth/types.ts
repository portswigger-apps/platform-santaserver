// src/lib/auth/types.ts
// CONFIRMED: Backend Enums (app/models/auth.py)

export enum UserType {
  LOCAL = 'local',   // UserTypeEnum.LOCAL
  SSO = 'sso',      // UserTypeEnum.SSO (future)
  SCIM = 'scim'     // UserTypeEnum.SCIM (future)
}

export enum ProviderType {
  SAML2 = 'saml2',     // ProviderTypeEnum.SAML2
  OIDC = 'oidc',       // ProviderTypeEnum.OIDC
  SCIM_V2 = 'scim_v2'  // ProviderTypeEnum.SCIM_V2
}

// CONFIRMED: Backend Schema (app/schemas/auth.py - UserProfile/UserResponse)
export interface User {
  id: string;           // UUID from backend
  username: string;
  email: string;
  user_type: UserType;  // 'local', 'sso', 'scim'
  
  // Profile fields (from UserProfile schema)
  first_name?: string;
  last_name?: string;
  display_name?: string;
  department?: string;
  title?: string;
  phone?: string;
  
  // Status fields (from UserResponse schema) 
  is_active: boolean;
  is_provisioned: boolean;  // Only in UserResponse
  last_login?: Date;
  created_at?: Date;        // Only in UserResponse
  updated_at?: Date;        // Only in UserResponse
  
  // Note: Backend doesn't include roles/groups in v1
  // These would be fetched separately via /users/{id}/roles endpoint (future)
}

export interface Role {
  id: string;
  name: string;
  display_name: string;
  permissions: Record<string, string[]>;
}

export interface Group {
  id: string;
  name: string;
  display_name: string;
  description?: string;
  source_type: 'local' | 'scim' | 'sso';
  external_id?: string;
  provider_name?: string;
  provider_display_name?: string;
  last_sync?: Date;
  roles: Role[];
}

export interface AuthProvider {
  id: string;
  name: string;
  display_name: string;
  provider_type: ProviderType;
  is_enabled: boolean;
  created_at: Date;
  updated_at: Date;
}

// CONFIRMED: Backend API Contract (app/schemas/auth.py)
export interface LoginRequest {
  username: string;  // Backend accepts username OR email
  password: string;  // Min 8 chars, complexity enforced backend
  // Note: remember_me not implemented in backend v1
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RefreshRequest {
  refresh_token: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}