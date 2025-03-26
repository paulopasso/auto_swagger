/**
 * @openapi
 * /auth/login:
 *   post:
 *     summary: Log in with email/password or OAuth
 *     description: Authenticate a user either via credentials or an external OAuth provider.
 *     tags:
 *       - Auth
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             oneOf:
 *               - $ref: '#/components/schemas/LoginWithEmail'
 *               - $ref: '#/components/schemas/LoginWithOAuth'
 *             discriminator:
 *               propertyName: type
 *               mapping:
 *                 credentials: '#/components/schemas/LoginWithEmail'
 *                 oauth: '#/components/schemas/LoginWithOAuth'
 *     responses:
 *       200:
 *         description: Successful login
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/AuthToken'
 *       401:
 *         description: Invalid credentials
 */
app.post('/auth/login', (req, res) => {
    const { type } = req.body;
  
    if (type === 'credentials') {
      const { email, password } = req.body;
      if (email === 'demo@example.com' && password === 'secure') {
        return res.json({ token: 'jwt.token.here' });
      }
    } else if (type === 'oauth') {
      const { provider, oauthToken } = req.body;
      if (provider === 'google' && oauthToken === 'valid_token') {
        return res.json({ token: 'oauth.jwt.token' });
      }
    }
  
    res.status(401).json({ message: 'Invalid login' });
  });
  