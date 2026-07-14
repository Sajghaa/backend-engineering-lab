import request from 'supertest';
import express from 'express';
import authRoutes from '../routes/auth.routes';
import db from '../database';

const app = express();
app.use(express.json());
app.use('/auth', authRoutes);

beforeEach(() => {
  // Clear users table before each test
  db.exec('DELETE FROM users');
});

describe('Auth API', () => {
  it('should register a new user', async () => {
    const res = await request(app)
      .post('/auth/register')
      .send({ email: 'test@test.com', username: 'test', password: 'secret' });
    expect(res.status).toBe(201);
    expect(res.body.username).toBe('test');
  });

  it('should login and return a token', async () => {
    await request(app)
      .post('/auth/register')
      .send({ email: 'test@test.com', username: 'test', password: 'secret' });
    const res = await request(app)
      .post('/auth/login')
      .send({ username: 'test', password: 'secret' });
    expect(res.status).toBe(200);
    expect(res.body.access_token).toBeDefined();
  });
});