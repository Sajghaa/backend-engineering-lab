import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import db from '../database';
import { config } from '../config';

interface User {
  id: number;
  email: string;
  username: string;
  hashed_password: string;
  is_active: number;
  role: string;
}

export interface UserPayload {
  id: number;
  username: string;
  role: string;
}

export const AuthService = {
  hashPassword(password: string): string {
    return bcrypt.hashSync(password, 10);
  },

  comparePassword(password: string, hash: string): boolean {
    return bcrypt.compareSync(password, hash);
  },

  createUser(email: string, username: string, password: string, role: string = 'user'): User {
    const hashed = this.hashPassword(password);
    const stmt = db.prepare(
      'INSERT INTO users (email, username, hashed_password, role) VALUES (?, ?, ?, ?)'
    );
    const result = stmt.run(email, username, hashed, role);
    return db.prepare('SELECT * FROM users WHERE id = ?').get(result.lastInsertRowid) as User;
  },

  getUserByUsername(username: string): User | undefined {
    return db.prepare('SELECT * FROM users WHERE username = ?').get(username) as User | undefined;
  },

  getUserById(id: number): User | undefined {
    return db.prepare('SELECT * FROM users WHERE id = ?').get(id) as User | undefined;
  },

  generateToken(user: User): string {
    const payload: UserPayload = {
      id: user.id,
      username: user.username,
      role: user.role,
    };
    return jwt.sign(payload, config.jwtSecret, { expiresIn: '30m' });
  },

  verifyToken(token: string): UserPayload {
    return jwt.verify(token, config.jwtSecret) as UserPayload;
  },
};