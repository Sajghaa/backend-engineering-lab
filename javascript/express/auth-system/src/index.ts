import express from 'express';
import { config } from './config';
import authRoutes from './routes/auth.routes';

const app = express();

// Middleware to parse JSON bodies
app.use(express.json());

// Routes
app.use('/auth', authRoutes);

app.get('/', (req, res) => {
  res.json({ message: 'Auth System API is running' });
});

app.listen(config.port, () => {
  console.log(`Server running on http://localhost:${config.port}`);
});