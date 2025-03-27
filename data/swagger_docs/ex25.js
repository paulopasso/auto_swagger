/**
 * @openapi
 * /documents/process:
 *   post:
 *     summary: Submit document for async processing
 *     description: |
 *       Uploads a document to be processed asynchronously. When processing is complete, the system will call back to the client's URL.
 *     tags:
 *       - Documents
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/DocumentProcessRequest'
 *     responses:
 *       202:
 *         description: Processing started
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/JobCreated'
 *     callbacks:
 *       onProcessed:
 *         '{$request.body.callbackUrl}':
 *           post:
 *             summary: Document processed callback
 *             description: |
 *               The system will call this URL once document processing is complete.
 *             requestBody:
 *               required: true
 *               content:
 *                 application/json:
 *                   schema:
 *                     $ref: '#/components/schemas/DocumentProcessedEvent'
 *             responses:
 *               200:
 *                 description: Acknowledged
 */
app.post('/documents/process', (req, res) => {
    const jobId = Math.floor(Math.random() * 100000);
    res.status(202).json({ jobId });
  });
  