/**
 * @openapi
 * /admin/users/bulk:
 *   post:
 *     summary: Bulk create users
 *     description: |
 *       Create multiple users in a single request. Returns a detailed report with status for each user.
 *       This endpoint is ideal for admins importing large datasets.
 *     tags:
 *       - Admin
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: array
 *             items:
 *               $ref: '#/components/schemas/NewUser'
 *     responses:
 *       207:
 *         description: Partial success or failure
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/BulkOperationResult'
 *       401:
 *         description: Unauthorized
 */
app.post('/admin/users/bulk', (req, res) => {
    const users = req.body;
  
    const result = users.map((user, index) => {
      if (!user.email || !user.role) {
        return {
          index,
          status: 'failed',
          error: 'Missing required fields'
        };
      }
  
      return {
        index,
        status: 'success',
        user: {
          id: Math.floor(Math.random() * 10000),
          ...user
        }
      };
    });
  
    res.status(207).json({ results: result });
  });
  