/**
 * @openapi
 * /me:
 *   get:
 *     summary: Get current user profile
 *     description: |
 *       Returns the authenticated user's profile. The shape of the response depends on the user's role:
       admin users get extra permissions info, while standard users get a simpler structure.
 *     tags:
 *       - Users
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Current user info
 *         content:
 *           application/json:
 *             schema:
 *               oneOf:
 *                 - $ref: '#/components/schemas/AdminUser'
 *                 - $ref: '#/components/schemas/StandardUser'
 *               discriminator:
 *                 propertyName: role
 *                 mapping:
 *                   admin: '#/components/schemas/AdminUser'
 *                   standard: '#/components/schemas/StandardUser'
 */
       app.get('/me', (req, res) => {
        const isAdmin = true;
      
        if (isAdmin) {
          return res.json({
            id: 1,
            name: 'Alice Admin',
            email: 'admin@example.com',
            role: 'admin',
            permissions: ['manage_users', 'view_reports']
          });
        }
      
        res.json({
          id: 2,
          name: 'Bob User',
          email: 'bob@example.com',
          role: 'standard'
        });
      });
      