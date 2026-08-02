export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export const STORE_RENDERER_URL = process.env.NEXT_PUBLIC_STORE_RENDERER_URL || 'http://localhost:3002';

export interface ReadinessCheck {
  key: string;
  label: string;
  status: 'pass' | 'partial' | 'fail';
  score: number;
  max_score: number;
  message: string;
}

export interface ReadinessReport {
  overall_score: number;
  checks: ReadinessCheck[];
  remaining_actions: string[];
  is_ready: boolean;
}

export interface StoreListItem {
  id: number;
  store_name: string;
  store_description: string;
  tagline: string | null;
  validation_score: number;
  created_at: string;
  blueprint_json: Record<string, any>;
  readiness?: ReadinessReport;
  shopify_readiness?: ReadinessReport;
}

export interface StoreListResponse {
  items: StoreListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface ValidationReport {
  generated_at: string;
  stores: number;
  averages: Record<string, number>;
  diversity: {
    overall_diversity_score: number;
    brand_diversity: number;
    prompt_diversity: number;
    content_diversity: number;
    cta_diversity: number;
    faq_diversity: number;
    average_similarity: number;
    best_case: number;
    worst_case: number;
    distribution: { range: string; count: number }[];
    similar_pairs?: { store_a: string; store_b: string; similarity: number; reason: string; recommendation: string }[];
  };
  per_store: Record<string, any>[];
}

export interface LaunchResponse {
  success: boolean;
  steps: { key: string; label: string; status: 'pending' | 'running' | 'completed' | 'failed'; detail?: string }[];
  storeId?: number;
  store_name?: string;
  readiness?: ReadinessReport;
  shopify_readiness?: ReadinessReport;
  error?: string;
}

export interface DashboardStats {
  total_stores: number;
  average_validation_score: number;
  recent_stores: { id: number; store_name: string; validation_score: number; created_at: string }[];
  ai_usage_count: number;
  plan_distribution: Record<string, number>;
}

export interface SystemStatus {
  health: {
    status: string;
    app: string;
    version: string;
    database: { status: string };
    redis: { status: string };
  };
  metrics: Record<string, { count: number; errors: number; avg_ms: number }>;
  environment: {
    debug: boolean;
    log_level: string;
    rate_limit_per_minute: number;
  };
}

export async function fetchStores(): Promise<StoreListResponse> {
  const response = await fetch(`${API_URL}/api/v1/stores/?page=1&page_size=50`, {
    cache: 'no-store',
  });
  if (!response.ok) {
    throw new Error(`Failed to load brands: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchValidationReport(): Promise<ValidationReport | null> {
  const response = await fetch(`${API_URL}/api/v1/validation/report`, {
    cache: 'no-store',
  });
  if (!response.ok) {
    return null;
  }
  return response.json();
}

export async function fetchDashboardStats(): Promise<DashboardStats | null> {
  const response = await fetch(`${API_URL}/api/v1/dashboard`, { cache: 'no-store' });
  if (!response.ok) {
    return null;
  }
  return response.json();
}

export async function fetchSystemStatus(): Promise<SystemStatus | null> {
  const response = await fetch(`${API_URL}/api/v1/admin/system-status`, { cache: 'no-store' });
  if (!response.ok) {
    return null;
  }
  return response.json();
}
