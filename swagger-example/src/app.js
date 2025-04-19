const express = require('express');
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const app = express();
const port = 3000;

// In-memory storage
const users = new Map();
const items = new Map();
let nextUserId = 1;
let nextItemId = 1;

// Swagger definition
const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Users and Items API',
      version: '1.0.0',
      description: 'A simple Express API with CRUD operations for users and items',
    },
    servers: [
      {
        url: 'http://localhost:3000',
        description: 'Development server',
      },
    ],
  },
  apis: ['./src/app.js'],
};

const swaggerDocs = swaggerJsdoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocs));

// Middleware for parsing JSON bodies
app.use(express.json());

// User Routes
app.post('/api/users', (req, res) => {
  const { name, email } = req.body;
  if (!name || !email) {
    return res.status(400).json({ error: 'Name and email are required' });
  }
  
  const id = nextUserId++;
  const newUser = {
    id,
    name,
    email,
    createdAt: new Date().toISOString()
  };
  users.set(id, newUser);
  res.status(201).json(newUser);
});

app.get('/api/users', (req, res) => {
  res.json(Array.from(users.values()));
});

app.get('/api/users/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const user = users.get(id);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  res.json(user);
});

app.put('/api/users/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const user = users.get(id);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }

  const { name, email } = req.body;
  if (!name && !email) {
    return res.status(400).json({ error: 'At least one field (name or email) must be provided' });
  }

  const updatedUser = {
    ...user,
    name: name || user.name,
    email: email || user.email,
  };
  users.set(id, updatedUser);
  res.json(updatedUser);
});

app.delete('/api/users/:id', (req, res) => {
  const id = parseInt(req.params.id);
  if (!users.has(id)) {
    return res.status(404).json({ error: 'User not found' });
  }
  users.delete(id);
  res.status(204).send();
});

// Item Routes
app.post('/api/items', (req, res) => {
  const { name, description, price, category } = req.body;
  if (!name || !description || price === undefined) {
    return res.status(400).json({ error: 'Name, description, and price are required' });
  }

  const id = nextItemId++;
  const newItem = {
    id,
    name,
    description,
    price,
    category: category || 'uncategorized',
    createdAt: new Date().toISOString()
  };
  items.set(id, newItem);
  res.status(201).json(newItem);
});

app.get('/api/items', (req, res) => {
  const { category } = req.query;
  let itemsList = Array.from(items.values());
  
  if (category) {
    itemsList = itemsList.filter(item => item.category === category);
  }
  
  res.json(itemsList);
});

app.get('/api/items/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const item = items.get(id);
  if (!item) {
    return res.status(404).json({ error: 'Item not found' });
  }
  res.json(item);
});

app.put('/api/items/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const item = items.get(id);
  if (!item) {
    return res.status(404).json({ error: 'Item not found' });
  }

  const { name, description, price, category } = req.body;
  if (!name && !description && price === undefined && !category) {
    return res.status(400).json({ error: 'At least one field must be provided for update' });
  }

  const updatedItem = {
    ...item,
    name: name || item.name,
    description: description || item.description,
    price: price !== undefined ? price : item.price,
    category: category || item.category
  };
  items.set(id, updatedItem);
  res.json(updatedItem);
});

app.delete('/api/items/:id', (req, res) => {
  const id = parseInt(req.params.id);
  if (!items.has(id)) {
    return res.status(404).json({ error: 'Item not found' });
  }
  items.delete(id);
  res.status(204).send();
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
  console.log(`Swagger documentation available at http://localhost:${port}/api-docs`);
}); 