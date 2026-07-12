const Message = require('../models/Message');

exports.getAllMessages = (req, res, next) => {
  try {
    const messages = Message.getAll();
    res.json({ success: true, data: messages });
  } catch (err) {
    next(err);
  }
};

exports.getMessageById = (req, res, next) => {
  try {
    const id = parseInt(req.params.id);
    const msg = Message.getById(id);
    if (!msg) {
      return res.status(404).json({ success: false, error: 'Message not found' });
    }
    res.json({ success: true, data: msg });
  } catch (err) {
    next(err);
  }
};

exports.createMessage = (req, res, next) => {
  try {
    const { user, text } = req.body;
    const msg = Message.create(user, text);
    res.status(201).json({ success: true, data: msg });
  } catch (err) {
    next(err);
  }
};

exports.deleteMessage = (req, res, next) => {
  try {
    const id = parseInt(req.params.id);
    const deleted = Message.delete(id);
    if (!deleted) {
      return res.status(404).json({ success: false, error: 'Message not found' });
    }
    res.json({ success: true, data: {} });
  } catch (err) {
    next(err);
  }
};