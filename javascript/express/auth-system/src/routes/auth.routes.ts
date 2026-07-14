import { Router, Request, Response } from 'express';
import { AuthService } from '../services/auth.service';
import { authenticate, requireRole } from '../middleware/auth.middleware';

const router = Router();

// POST /auth/register
router.post('/register', (req: Request, res: Response) => {
  const { email, username, password, role } = req.body;
  if (!email || !username || !password) {
    return res.status(400).json({ message: 'Missing fields' });
  }
  try {
    const user = AuthService.createUser(email, username, password, role || 'user');
    // Don't return the hashed password
    const { hashed_password, ...userWithoutPassword } = user;
    return res.status(201).json(userWithoutPassword);
  } catch (err: any) {
    if (err.message.includes('UNIQUE constraint')) {
      return res.status(400).json({ message: 'Username or email already exists' });
    }
    return res.status(500).json({ message: 'Internal server error' });
  }
});

// POST /auth/login
router.post('/login', (req: Request, res: Response) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ message: 'Missing username or password' });
  }
  const user = AuthService.getUserByUsername(username);
  if (!user || !AuthService.comparePassword(password, user.hashed_password)) {
    return res.status(401).json({ message: 'Invalid credentials' });
  }
  const token = AuthService.generateToken(user);
  return res.json({ access_token: token, token_type: 'bearer' });
});

// GET /auth/me
router.get('/me', authenticate, (req: Request, res: Response) => {
  const user = AuthService.getUserById(req.user!.id);
  if (!user) {
    return res.status(404).json({ message: 'User not found' });
  }
  const { hashed_password, ...userWithoutPassword } = user;
  return res.json(userWithoutPassword);
});

// GET /auth/admin-only
router.get('/admin-only', authenticate, requireRole('admin'), (req: Request, res: Response) => {
  return res.json({ message: 'Welcome admin!', user: req.user!.username });
});

export default router;