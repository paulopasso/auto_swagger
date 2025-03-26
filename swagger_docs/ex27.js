/**
 * @openapi
 * /admin/users:
 *   post:
 *     summary: Create a new user (admin only)
 *     description: |
 *       Creates a new user account. This endpoint is restricted to users with the `admin` role.
 *     tags:
 *       - Admin
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/NewUser'
 *     responses:
 *       201:
 *         description: User created successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/User'
 *       403:
 *         description: Forbidden - insufficient permissions
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 */
app.post('/admin/users', (req, res) => {
    const userRole = 'manager'; // simulate access check
  
    if (userRole !== 'admin') {
      return res.status(403).json({
        error: 'FORBIDDEN',
        message: 'Only admins can create users.'
      });
    }
  
    const newUser = {
      id: 300,
      name: req.body.name,
      email: req.body.email,
      role: req.body.role
    };
  
    res.status(201).json(newUser);
  });
  