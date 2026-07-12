const express = require('express');
const { body, param, validationResult } = require('express-validator');
const controller = require('../controllers/messageController');

const router = express.Router();

// Middleware to handle validation errors
const validate = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ success: false, errors: errors.array() });
  }
  next();
};

router.get('/', controller.getAllMessages);

router.get('/:id',
  param('id').isInt({ min: 1 }).withMessage('ID must be a positive integer'),
  validate,
  controller.getMessageById
);

router.post('/',
  body('user').trim().notEmpty().withMessage('User is required'),
  body('text').trim().notEmpty().withMessage('Text is required'),
  validate,
  controller.createMessage
);

router.delete('/:id',
  param('id').isInt({ min: 1 }).withMessage('ID must be a positive integer'),
  validate,
  controller.deleteMessage
);

module.exports = router;