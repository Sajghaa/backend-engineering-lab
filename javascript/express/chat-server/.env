// src/models/Message.js
const messages = [];
let nextId = 1;

class Message {
  constructor(user, text) {
    this.id = nextId++;
    this.user = user;
    this.text = text;
    this.timestamp = new Date().toISOString();
  }

  static getAll() {
    return messages;
  }

  static getById(id) {
    return messages.find(m => m.id === id);
  }

  static create(user, text) {
    const msg = new Message(user, text);
    messages.push(msg);
    return msg;
  }

  static delete(id) {
    const index = messages.findIndex(m => m.id === id);
    if (index !== -1) {
      messages.splice(index, 1);
      return true;
    }
    return false;
  }
}

module.exports = Message;