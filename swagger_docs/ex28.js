const express = require('express');
const app = express();
app.use(express.json());

/**
 * @openapi
 * /public/data:
 *   get:
 *     summary: Access public data with API key
 *     description: |
 *       Retrieve read-only public data using an API key. This is ideal for CLI tools, read-only SDKs, and third-party integrations.
 *     tags:
 *       - Public
 *     security:
 *       - apiKeyAuth: []
 *     responses:
 *       200:
 *         description: Public data response
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: "Public data response"
 *       401:
 *         description: Missing or invalid API key
 */
app.get('/public/data', (req, res) => {
  const apiKey = req.headers['x-api-key'];
  if (apiKey !== 'valid-api-key') {
    return res.status(401).json({ message: 'Invalid API key' });
  }

  res.json({ message: 'Public data response' });
});

/**
 * @openapi
 * /user/profile:
 *   get:
 *     summary: Get authenticated user profile
 *     description: Requires a Bearer token to return the current user's profile.
 *     tags:
 *       - Users
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: User profile
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/User'
 */
app.get('/user/profile', (req, res) => {
  const auth = req.headers['authorization'];
  if (!auth || !auth.startsWith('Bearer ') || auth !== 'Bearer mysecrettoken') {
    return res.status(401).json({ message: 'Unauthorized' });
  }

  res.json({
    id: 42,
    name: 'Gemini User',
    email: 'gemini@openai.com'
  });
});

/**
 * @openapi
 * /billing/transactions:
 *   get:
 *     summary: Get billing transactions
 *     description: Requires OAuth2 with `read:billing` scope.
 *     tags:
 *       - Billing
 *     security:
 *       - oauth2:
 *           - read:billing
 *     responses:
 *       200:
 *         description: Billing history
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Transaction'
 */
app.get('/billing/transactions', (req, res) => {
  // Simulated OAuth2 token + scope validation
  const tokenScopes = ['read:billing']; // hardcoded example
  if (!tokenScopes.includes('read:billing')) {
    return res.status(403).json({ message: 'Missing read:billing scope' });
  }

  res.json([
    {
      id: 891,
      amount: 149.95,
      date: '2025-03-26T10:30:00Z'
    },
    {
      id: 892,
      amount: 299.00,
      date: '2025-03-24T08:15:00Z'
    }
  ]);
});

// Run the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Mock API running on port ${PORT}`));
