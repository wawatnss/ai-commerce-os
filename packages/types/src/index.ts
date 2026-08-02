// Core Domain Types

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'moderator';
  createdAt: Date;
  updatedAt: Date;
}

export interface Store {
  id: string;
  userId: string;
  name: string;
  domain: string;
  description: string;
  logo?: string;
  theme: StoreTheme;
  settings: StoreSettings;
  status: 'active' | 'inactive' | 'suspended';
  createdAt: Date;
  updatedAt: Date;
}

export interface StoreTheme {
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  fontFamily: string;
  customCSS?: string;
}

export interface StoreSettings {
  currency: string;
  language: string;
  timezone: string;
  enableBlog: boolean;
  enableFAQ: boolean;
  enableContact: boolean;
}

export interface Product {
  id: string;
  storeId: string;
  name: string;
  description: string;
  sku: string;
  price: number;
  compareAtPrice?: number;
  costPrice?: number;
  images: ProductImage[];
  variants: ProductVariant[];
  categories: string[];
  tags: string[];
  metadata: ProductMetadata;
  status: 'draft' | 'active' | 'archived';
  createdAt: Date;
  updatedAt: Date;
}

export interface ProductImage {
  id: string;
  url: string;
  alt: string;
  position: number;
}

export interface ProductVariant {
  id: string;
  name: string;
  price: number;
  sku: string;
  inventory: number;
  attributes: Record<string, string>;
}

export interface ProductMetadata {
  margin: number;
  competitionScore: number;
  marketInterest: number;
  shippingEase: number;
  contentPotential: number;
  seasonality: number;
  overallScore: number;
  sources: string[];
}

export interface Trend {
  id: string;
  keyword: string;
  source: string;
  volume: number;
  growth: number;
  category: string;
  relatedKeywords: string[];
  detectedAt: Date;
  expiresAt: Date;
}

export interface Brand {
  id: string;
  storeId: string;
  name: string;
  tagline: string;
  description: string;
  identity: BrandIdentity;
  voice: BrandVoice;
  createdAt: Date;
  updatedAt: Date;
}

export interface BrandIdentity {
  logo: string;
  colorPalette: ColorPalette;
  typography: Typography;
  visualStyle: string;
}

export interface ColorPalette {
  primary: string;
  secondary: string;
  accent: string;
  neutral: string[];
}

export interface Typography {
  headingFont: string;
  bodyFont: string;
  accentFont?: string;
}

export interface BrandVoice {
  tone: 'professional' | 'casual' | 'friendly' | 'luxury' | 'minimalist';
  style: string;
  guidelines: string[];
}

export interface Content {
  id: string;
  storeId: string;
  type: 'blog' | 'product' | 'page' | 'meta';
  title: string;
  body: string;
  metadata: ContentMetadata;
  status: 'draft' | 'published' | 'archived';
  publishedAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface ContentMetadata {
  seoTitle: string;
  seoDescription: string;
  keywords: string[];
  canonicalUrl?: string;
  ogImage?: string;
  schema?: Record<string, any>;
}

export interface Analytics {
  storeId: string;
  period: AnalyticsPeriod;
  metrics: AnalyticsMetrics;
  topProducts: ProductAnalytics[];
  topContent: ContentAnalytics[];
  trafficSources: TrafficSource[];
  conversions: ConversionData[];
}

export interface AnalyticsPeriod {
  start: Date;
  end: Date;
}

export interface AnalyticsMetrics {
  visitors: number;
  pageViews: number;
  sessions: number;
  bounceRate: number;
  avgSessionDuration: number;
  conversions: number;
  revenue: number;
  conversionRate: number;
}

export interface ProductAnalytics {
  productId: string;
  productName: string;
  views: number;
  addToCart: number;
  purchases: number;
  revenue: number;
  conversionRate: number;
}

export interface ContentAnalytics {
  contentId: string;
  contentTitle: string;
  views: number;
  shares: number;
  comments: number;
  avgTimeOnPage: number;
}

export interface TrafficSource {
  source: string;
  visitors: number;
  percentage: number;
}

export interface ConversionData {
  funnel: string;
  stage: string;
  count: number;
  dropOffRate: number;
}

// AI Provider Types

export interface AIProvider {
  name: 'openai' | 'anthropic' | 'custom';
  apiKey: string;
  model: string;
  config?: Record<string, any>;
}

export interface AIRequest {
  provider: AIProvider['name'];
  prompt: string;
  systemPrompt?: string;
  temperature?: number;
  maxTokens?: number;
  context?: Record<string, any>;
}

export interface AIResponse {
  content: string;
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  model: string;
  provider: AIProvider['name'];
}

// API Types

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ApiError;
  meta?: Record<string, any>;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface PaginationParams {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Service Types

export interface ServiceConfig {
  enabled: boolean;
  config: Record<string, any>;
}

export interface TrendIntelligenceConfig extends ServiceConfig {
  sources: string[];
  updateInterval: number;
  minVolume: number;
  minGrowth: number;
}

export interface ProductIntelligenceConfig extends ServiceConfig {
  evaluationCriteria: string[];
  autoEvaluation: boolean;
  evaluationInterval: number;
}

export interface BrandBuilderConfig extends ServiceConfig {
  aiProvider: AIProvider['name'];
  stylePresets: string[];
}

export interface StoreBuilderConfig extends ServiceConfig {
  templates: string[];
  defaultFeatures: string[];
}

export interface SEOEngineConfig extends ServiceConfig {
  autoOptimization: boolean;
  keywordTracking: boolean;
  competitorAnalysis: boolean;
}

export interface ContentEngineConfig extends ServiceConfig {
  autoGeneration: boolean;
  contentTypes: string[];
  generationInterval: number;
}

export interface AnalyticsConfig extends ServiceConfig {
  trackingEnabled: boolean;
  realTime: boolean;
  retentionDays: number;
}

export interface CustomerSupportConfig extends ServiceConfig {
  aiProvider: AIProvider['name'];
  knowledgeBase: string;
  escalationRules: string[];
}

// Agent Types

export interface Agent {
  id: string;
  name: string;
  type: AgentType;
  status: 'idle' | 'running' | 'paused' | 'error';
  config: AgentConfig;
  lastRun?: Date;
  nextRun?: Date;
}

export type AgentType =
  | 'trend-analyst'
  | 'product-evaluator'
  | 'brand-creator'
  | 'store-generator'
  | 'seo-optimizer'
  | 'content-writer'
  | 'support-assistant';

export interface AgentConfig {
  schedule?: AgentSchedule;
  triggers?: AgentTrigger[];
  parameters: Record<string, any>;
}

export interface AgentSchedule {
  frequency: 'once' | 'hourly' | 'daily' | 'weekly' | 'monthly';
  cronExpression?: string;
  timezone: string;
}

export interface AgentTrigger {
  type: 'event' | 'webhook' | 'manual';
  condition?: string;
}

export interface AgentExecution {
  id: string;
  agentId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  input: Record<string, any>;
  output?: Record<string, any>;
  error?: string;
  startedAt: Date;
  completedAt?: Date;
  duration?: number;
}
