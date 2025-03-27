/**
 * @openapi
 * /org/users:
 *   get:
 *     summary: List users in the organization
 *     description: |
 *       Retrieve all users that belong to the organization identified by the `X-Org-ID` header.
 *       This endpoint is part of a multi-tenant architecture and requires proper scoping.
 *     tags:
 *       - Organization
 *     parameters:
 *       - in: header
 *         name: X-Org-ID
 *         required: true
 *         schema:
 *           type: string
 *         description: Unique identifier of the organization
 *     responses:
 *       200:
 *         description: List of users in the organization
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/User'
 *       400:
 *         description: Missing or invalid organization header
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 */
app.get('/org/users', (req, res) => {
    const orgId = req.headers['x-org-id'];
    if (!orgId) {
      return res.status(400).json({
        error: 'ORG_HEADER_MISSING',
        message: 'X-Org-ID header is required for tenant scoping'
      });
    }
  
    const users = [
      { id: 1, name: 'Admin', email: 'admin@org.com' },
      { id: 2, name: 'User', email: 'user@org.com' }
    ];
  
    res.status(200).json(users);
  });
  