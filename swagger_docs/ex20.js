/**
 * @openapi
 * /reports:
 *   post:
 *     summary: Request a new report
 *     description: |
 *       Starts the generation of a report asynchronously.
 *       The client should poll the job status using the returned job ID.
 *     tags:
 *       - Reports
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/ReportRequest'
 *     responses:
 *       202:
 *         description: Report generation started
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/JobCreated'
 */
app.post('/reports', (req, res) => {
    const jobId = Math.floor(Math.random() * 100000);
    res.status(202).json({ jobId });
  });
  
  /**
   * @openapi
   * /jobs/{id}/status:
   *   get:
   *     summary: Check job status
   *     description: Poll the status of a long-running job.
   *     tags:
   *       - Reports
   *     parameters:
   *       - in: path
   *         name: id
   *         required: true
   *         schema:
   *           type: integer
   *         description: The job ID
   *     responses:
   *       200:
   *         description: Job status info
   *         content:
   *           application/json:
   *             schema:
   *               $ref: '#/components/schemas/JobStatus'
   */
  app.get('/jobs/:id/status', (req, res) => {
    const jobId = parseInt(req.params.id);
    res.json({
      jobId,
      status: 'processing',
      progress: 42
    });
  });
  
  /**
   * @openapi
   * /jobs/{id}/result:
   *   get:
   *     summary: Get job result
   *     description: |
   *       Returns the result of the job once it's complete.
   *     tags:
   *       - Reports
   *     parameters:
   *       - in: path
   *         name: id
   *         required: true
   *         schema:
   *           type: integer
   *         description: The job ID
   *     responses:
   *       200:
   *         description: Job result
   *         content:
   *           application/json:
   *             schema:
   *               $ref: '#/components/schemas/ReportResult'
   *       425:
   *         description: Job not ready yet (Too Early)
   */
  app.get('/jobs/:id/result', (req, res) => {
    res.status(425).json({ message: 'Job still processing' });
  });
  