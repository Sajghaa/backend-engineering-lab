// src/app.js
const express = require('express');
const cors = require('cors');
const messageRoutes = require('./routes/messageRoutes');
const errorHandler = require('./middleware/errorHandler');

const app = express();

app.use(cors());
app.use(express.json());

app.use('/api/messages', messageRoutes);

app.get('/health', (req, res) => res.send('OK'));

app.use(errorHandler);

module.exports = app;   // ← must be exactly this