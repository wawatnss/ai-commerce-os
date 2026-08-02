import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';

let client: postgres.Sql | null = null;
let db: ReturnType<typeof drizzle> | null = null;

export function getDatabase(connectionString?: string) {
  if (!db) {
    const url = connectionString || process.env.DATABASE_URL;
    if (!url) {
      throw new Error('DATABASE_URL environment variable is not set');
    }
    client = postgres(url);
    db = drizzle(client, { schema });
  }
  return db;
}

export async function closeDatabase() {
  if (client) {
    await client.end();
    client = null;
    db = null;
  }
}

export * from './schema';
