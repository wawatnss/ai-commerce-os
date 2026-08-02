import { pgTable, serial, text, timestamp, varchar, boolean, jsonb, decimal, integer, index } from 'drizzle-orm/pg-core';

// Users table
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  name: varchar('name', { length: 255 }).notNull(),
  role: varchar('role', { length: 50 }).notNull().default('user'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
}, (table) => ({
  emailIdx: index('users_email_idx').on(table.email),
}));

// Stores table
export const stores = pgTable('stores', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').notNull().references(() => users.id),
  name: varchar('name', { length: 255 }).notNull(),
  domain: varchar('domain', { length: 255 }).notNull().unique(),
  description: text('description'),
  logo: text('logo'),
  theme: jsonb('theme').notNull().$type<{
    primaryColor: string;
    secondaryColor: string;
    accentColor: string;
    fontFamily: string;
    customCSS?: string;
  }>(),
  settings: jsonb('settings').notNull().$type<{
    currency: string;
    language: string;
    timezone: string;
    enableBlog: boolean;
    enableFAQ: boolean;
    enableContact: boolean;
  }>(),
  status: varchar('status', { length: 50 }).notNull().default('active'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
}, (table) => ({
  userIdIdx: index('stores_user_id_idx').on(table.userId),
  domainIdx: index('stores_domain_idx').on(table.domain),
}));

// Products table
export const products = pgTable('products', {
  id: serial('id').primaryKey(),
  storeId: integer('store_id').notNull().references(() => stores.id),
  name: varchar('name', { length: 255 }).notNull(),
  description: text('description').notNull(),
  sku: varchar('sku', { length: 100 }).notNull(),
  price: decimal('price', { precision: 10, scale: 2 }).notNull(),
  compareAtPrice: decimal('compare_at_price', { precision: 10, scale: 2 }),
  costPrice: decimal('cost_price', { precision: 10, scale: 2 }),
  images: jsonb('images').notNull().$type<Array<{
    id: string;
    url: string;
    alt: string;
    position: number;
  }>>(),
  variants: jsonb('variants').notNull().$type<Array<{
    id: string;
    name: string;
    price: number;
    sku: string;
    inventory: number;
    attributes: Record<string, string>;
  }>>(),
  categories: jsonb('categories').notNull().$type<string[]>(),
  tags: jsonb('tags').notNull().$type<string[]>(),
  metadata: jsonb('metadata').notNull().$type<{
    margin: number;
    competitionScore: number;
    marketInterest: number;
    shippingEase: number;
    contentPotential: number;
    seasonality: number;
    overallScore: number;
    sources: string[];
  }>(),
  status: varchar('status', { length: 50 }).notNull().default('draft'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
}, (table) => ({
  storeIdIdx: index('products_store_id_idx').on(table.storeId),
  skuIdx: index('products_sku_idx').on(table.sku),
  statusIdx: index('products_status_idx').on(table.status),
}));

// Trends table
export const trends = pgTable('trends', {
  id: serial('id').primaryKey(),
  keyword: varchar('keyword', { length: 255 }).notNull(),
  source: varchar('source', { length: 100 }).notNull(),
  volume: integer('volume').notNull(),
  growth: decimal('growth', { precision: 5, scale: 2 }).notNull(),
  category: varchar('category', { length: 100 }),
  relatedKeywords: jsonb('related_keywords').notNull().$type<string[]>(),
  detectedAt: timestamp('detected_at').notNull().defaultNow(),
  expiresAt: timestamp('expires_at'),
}, (table) => ({
  keywordIdx: index('trends_keyword_idx').on(table.keyword),
  sourceIdx: index('trends_source_idx').on(table.source),
  categoryIdx: index('trends_category_idx').on(table.category),
  detectedAtIdx: index('trends_detected_at_idx').on(table.detectedAt),
}));

// Brands table
export const brands = pgTable('brands', {
  id: serial('id').primaryKey(),
  storeId: integer('store_id').notNull().references(() => stores.id),
  name: varchar('name', { length: 255 }).notNull(),
  tagline: varchar('tagline', { length: 500 }),
  description: text('description'),
  identity: jsonb('identity').notNull().$type<{
    logo: string;
    colorPalette: {
      primary: string;
      secondary: string;
      accent: string;
      neutral: string[];
    };
    typography: {
      headingFont: string;
      bodyFont: string;
      accentFont?: string;
    };
    visualStyle: string;
  }>(),
  voice: jsonb('voice').notNull().$type<{
    tone: 'professional' | 'casual' | 'friendly' | 'luxury' | 'minimalist';
    style: string;
    guidelines: string[];
  }>(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
}, (table) => ({
  storeIdIdx: index('brands_store_id_idx').on(table.storeId),
}));

// Content table
export const content = pgTable('content', {
  id: serial('id').primaryKey(),
  storeId: integer('store_id').notNull().references(() => stores.id),
  type: varchar('type', { length: 50 }).notNull(),
  title: varchar('title', { length: 255 }).notNull(),
  body: text('body').notNull(),
  metadata: jsonb('metadata').notNull().$type<{
    seoTitle: string;
    seoDescription: string;
    keywords: string[];
    canonicalUrl?: string;
    ogImage?: string;
    schema?: Record<string, any>;
  }>(),
  status: varchar('status', { length: 50 }).notNull().default('draft'),
  publishedAt: timestamp('published_at'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
}, (table) => ({
  storeIdIdx: index('content_store_id_idx').on(table.storeId),
  typeIdx: index('content_type_idx').on(table.type),
  statusIdx: index('content_status_idx').on(table.status),
  publishedAtIdx: index('content_published_at_idx').on(table.publishedAt),
}));

// Analytics table
export const analytics = pgTable('analytics', {
  id: serial('id').primaryKey(),
  storeId: integer('store_id').notNull().references(() => stores.id),
  period: jsonb('period').notNull().$type<{
    start: Date;
    end: Date;
  }>(),
  metrics: jsonb('metrics').notNull().$type<{
    visitors: number;
    pageViews: number;
    sessions: number;
    bounceRate: number;
    avgSessionDuration: number;
    conversions: number;
    revenue: number;
    conversionRate: number;
  }>(),
  topProducts: jsonb('top_products').notNull().$type<Array<{
    productId: string;
    productName: string;
    views: number;
    addToCart: number;
    purchases: number;
    revenue: number;
    conversionRate: number;
  }>>(),
  topContent: jsonb('top_content').notNull().$type<Array<{
    contentId: string;
    contentTitle: string;
    views: number;
    shares: number;
    comments: number;
    avgTimeOnPage: number;
  }>>(),
  trafficSources: jsonb('traffic_sources').notNull().$type<Array<{
    source: string;
    visitors: number;
    percentage: number;
  }>>(),
  conversions: jsonb('conversions').notNull().$type<Array<{
    funnel: string;
    stage: string;
    count: number;
    dropOffRate: number;
  }>>(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
}, (table) => ({
  storeIdIdx: index('analytics_store_id_idx').on(table.storeId),
  periodIdx: index('analytics_period_idx').on(table.period),
}));

// Agents table
export const agents = pgTable('agents', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 255 }).notNull(),
  type: varchar('type', { length: 100 }).notNull(),
  status: varchar('status', { length: 50 }).notNull().default('idle'),
  config: jsonb('config').notNull().$type<{
    schedule?: {
      frequency: 'once' | 'hourly' | 'daily' | 'weekly' | 'monthly';
      cronExpression?: string;
      timezone: string;
    };
    triggers?: Array<{
      type: 'event' | 'webhook' | 'manual';
      condition?: string;
    }>;
    parameters: Record<string, any>;
  }>(),
  lastRun: timestamp('last_run'),
  nextRun: timestamp('next_run'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
}, (table) => ({
  typeIdx: index('agents_type_idx').on(table.type),
  statusIdx: index('agents_status_idx').on(table.status),
}));

// Agent executions table
export const agentExecutions = pgTable('agent_executions', {
  id: serial('id').primaryKey(),
  agentId: integer('agent_id').notNull().references(() => agents.id),
  status: varchar('status', { length: 50 }).notNull().default('pending'),
  input: jsonb('input').notNull().$type<Record<string, any>>(),
  output: jsonb('output').$type<Record<string, any>>(),
  error: text('error'),
  startedAt: timestamp('started_at').notNull().defaultNow(),
  completedAt: timestamp('completed_at'),
  duration: integer('duration'),
}, (table) => ({
  agentIdIdx: index('agent_executions_agent_id_idx').on(table.agentId),
  statusIdx: index('agent_executions_status_idx').on(table.status),
  startedAtIdx: index('agent_executions_started_at_idx').on(table.startedAt),
}));

// Service configurations table
export const serviceConfigs = pgTable('service_configs', {
  id: serial('id').primaryKey(),
  service: varchar('service', { length: 100 }).notNull().unique(),
  enabled: boolean('enabled').notNull().default(true),
  config: jsonb('config').notNull().$type<Record<string, any>>(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
}, (table) => ({
  serviceIdx: index('service_configs_service_idx').on(table.service),
}));
