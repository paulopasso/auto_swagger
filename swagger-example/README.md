# Swagger Express.js Example

This is a simple Express.js API project that demonstrates how to integrate Swagger documentation.

## Features

- Express.js REST API
- Swagger UI documentation
- Example endpoints with full documentation
- JSON request/response handling

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Access the API:
- API endpoint: http://localhost:3000
- Swagger documentation: http://localhost:3000/api-docs

## Available Endpoints

- GET `/api/hello` - Returns a hello message
- POST `/api/users` - Creates a new user

## Testing the API

You can test the API using the Swagger UI interface or using curl:

```bash
# Test the hello endpoint
curl http://localhost:3000/api/hello

# Test creating a user
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
``` 