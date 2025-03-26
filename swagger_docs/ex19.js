/**
 * @openapi
 * /webhooks/register:
 *   post:
 *     summary: Register a webhook URL
 *     description: |
 *       Register a URL that will receive POST events when specific system actions occur.
 *       You must host an HTTPS endpoint that matches the expected callback format.
 *     tags:
 *       - Webhooks
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/WebhookRegistration'
 *     responses:
 *       201:
 *         description: Webhook registered
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/WebhookAck'
 *     callbacks:
 *       eventCallback:
 *         '{$request.body.url}':
 *           post:
 *             summary: Event callback receiver
 *             description: |
 *               This callback is triggered when a user account is deleted.
 *             requestBody:
 *               required: true
 *               content:
 *                 application/json:
 *                   schema:
 *                     $ref: '#/components/schemas/UserDeletedEvent'
 *             responses:
 *               200:
 *                 description: Acknowledged
 */
app.post('/webhooks/register', (req, res) => {
    const { url, event } = req.body;
    // Pretend we're saving it to the DB and will call it later
    res.status(201).json({ success: true, subscribedTo: event });
  });
  