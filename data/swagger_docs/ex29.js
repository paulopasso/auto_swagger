/**
 * @openapi
 * /org/users/{userId}:
 *   put:
 *     summary: Update a team member (admin role only, tenant-scoped)
 *     description: |
 *       Update a user within your organization. You must include a valid `X-Org-ID` header and be authenticated with the `admin` role.
 *     tags:
 *       - Organization
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: header
 *         name: X-Org-ID
 *         required: true
 *         schema:
 *           type: string
 *         description: Organization identifier for tenant scoping
 *       - in: path
 *         name: userId
 *         required: true
 *         schema:
 *           type: integer
 *         description: The user ID within the organization
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/UpdateUser'
 *     responses:
 *       200:
 *         description: User updated successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/User'
 *       400:
 *         description: Missing or invalid organization ID
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 *       403:
 *         description: Forbidden - role not authorized
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 */
app.put('/org/users/:userId', (req, res) => {
    const orgId = req.headers['x-org-id'];
    const userRole = 'viewer'; // Simulated user role
  
    if (!orgId) {
      return res.status(400).json({
        error: 'MISSING_ORG_HEADER',
        message: 'X-Org-ID header is required.'
      });
    }
  
    if (userRole !== 'admin') {
      return res.status(403).json({
        error: 'FORBIDDEN',
        message: 'You do not have permission to modify organization users.'
      });
    }
  
    res.json({
      id: parseInt(req.params.userId),
      name: req.body.name,
      email: req.body.email,
      role: req.body.role,
      orgId
    });
  });
  