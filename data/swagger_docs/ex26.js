/**
 * @openapi
 * /analytics/reports:
 *   get:
 *     summary: Get paginated analytics reports
 *     description: |
 *       Retrieves analytics reports for a given date range.
 *       Supports pagination and filtering using shared components for consistency across the API.
 *     tags:
 *       - Analytics
 *     parameters:
 *       - $ref: '#/components/parameters/Page'
 *       - $ref: '#/components/parameters/Limit'
 *       - $ref: '#/components/parameters/DateFrom'
 *       - $ref: '#/components/parameters/DateTo'
 *     responses:
 *       200:
 *         description: Paginated report results
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/PaginatedReports'
 *       400:
 *         description: Invalid query params
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 */
app.get('/analytics/reports', (req, res) => {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const reports = Array.from({ length: limit }, (_, i) => ({
      id: i + 1 + (page - 1) * limit,
      title: `Report #${i + 1}`,
      createdAt: new Date().toISOString()
    }));
  
    res.json({
      data: reports,
      meta: {
        page,
        limit,
        total: 100
      }
    });
  });
  