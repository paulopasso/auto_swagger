/**
 * @openapi
 * /admin/users:
 *   get:
 *     summary: Get list of users (admin only)
 *     description: |
 *       Retrieve a list of all users. This endpoint is protected by OAuth2 and only accessible to clients with the `read:users` scope.
 *     tags:
 *       - Admin
 *     security:
 *       - oauth2:
 *           - read:users
 *     responses:
 *       200:
 *         description: List of users
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/User'
 *       403:
 *         description: Forbidden - insufficient scope
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 */
app.get('/admin/users', (req, res) => {
    const tokenScopes = ['read:users']; // Simulated for demo purposes
    if (!tokenScopes.includes('read:users')) {
      return res.status(403).json({
        error: 'FORBIDDEN',
        message: 'You do not have the required scope: read:users'
      });
    }
  
    res.json([
      { id: 1, name: 'Alice Admin', email: 'alice@company.com' },
      { id: 2, name: 'Bob Mod', email: 'bob@company.com' }
    ]);
  });
  