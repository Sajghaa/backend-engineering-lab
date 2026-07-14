import Database from 'better-sqlite3';
import { config } from './config';

const db = new Database(config.dbPath);

// Enable WAL mode for better concurrency (optional)
db.pragma('journal_mode = WAL');

// Create users table if not exists
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    role TEXT DEFAULT 'user'
  )
`);

export default db;