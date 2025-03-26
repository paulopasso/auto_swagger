/**
 * @openapi
 * /me:
 *   get:
 *     summary: Get current user profile
 *     description: Retrieve the authenticated user's profile information.
 *     tags:
 *       - Users
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Authenticated user's profile
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/User'
 *       401:
 *         description: Unauthorized - missing or invalid token
 */
app.get('/me', (req, res) => {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ message: 'Unauthorized' });
    }
  
    // Mock authenticated user
    const user = {
      id: 7,
      name: 'Jane Doe',
      email: 'jane@example.com'
    };
  
    res.json(user);
  });
  