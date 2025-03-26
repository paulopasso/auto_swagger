/**
 * @openapi
 * /accounts/me:
 *   get:
 *     summary: Get current account info
 *     description: |
 *       Retrieves account information for the authenticated user.
 *       Supports versioning via custom headers and correlation via request ID.
 *     tags:
 *       - Accounts
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: header
 *         name: X-Request-ID
 *         schema:
 *           type: string
 *         required: false
 *         description: Optional unique ID for tracking the request
 *       - in: header
 *         name: X-API-Version
 *         schema:
 *           type: string
 *           enum: [v1, v2]
 *           default: v1
 *         required: false
 *         description: Specify the API version to use (default is v1)
 *     responses:
 *       200:
 *         description: Account info retrieved successfully
 *         headers:
 *           X-Request-ID:
 *             description: Echoes the request ID sent by the client
 *             schema:
 *               type: string
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Account'
 *       401:
 *         description: Unauthorized
 */
app.get('/accounts/me', (req, res) => {
    const requestId = req.headers['x-request-id'] || `req-${Date.now()}`;
    const version = req.headers['x-api-version'] || 'v1';
  
    const user = {
      id: 101,
      name: 'Jane API',
      versionUsed: version
    };
  
    res.setHeader('X-Request-ID', requestId);
    res.json(user);
  });
  