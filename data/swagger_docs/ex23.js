/**
 * @openapi
 * /users/{id}:
 *   patch:
 *     summary: Partially update user profile
 *     description: |
 *       Update one or more fields of the user's profile. Requires the authenticated user to have permission to update the target user.
 *     tags:
 *       - Users
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: The ID of the user to update
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/UserUpdate'
 *     responses:
 *       200:
 *         description: User updated successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/User'
 *       403:
 *         description: Forbidden - you don’t have permission
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 *       422:
 *         description: Validation failed
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ValidationError'
 */
app.patch('/users/:id', (req, res) => {
    const hasPermission = true; // Mock
    const { email } = req.body;
  
    if (!hasPermission) {
      return res.status(403).json({ error: 'FORBIDDEN', message: 'You cannot update this user.' });
    }
  
    if (email && !email.includes('@')) {
      return res.status(422).json({
        error: 'VALIDATION_FAILED',
        details: [
          {
            field: 'email',
            issue: 'Invalid email format'
          }
        ]
      });
    }
  
    res.json({
      id: parseInt(req.params.id),
      name: req.body.name || 'Unchanged',
      email: email || 'original@example.com'
    });
  });
  