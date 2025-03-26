
/**
 * @openapi
 * /messages/draft:
 *   post:
 *     summary: Generate email reply draft
 *     description: |
 *       Uses input context to generate a draft reply. This draft should be presented to the user before sending.
 *     tags:
 *       - LLM Tools
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/DraftRequest'
 *     responses:
 *       200:
 *         description: Draft generated
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/DraftResponse'
 */
app.post('/messages/draft', (req, res) => {
    const { originalMessage, recipient } = req.body;
  
    const draft = `Hi ${recipient.split('@')[0]},\n\nThanks for your message. I'd be happy to discuss further.\n\nBest,\nMe`;
  
    res.json({ draft });
  });
  
  /**
   * @openapi
   * /messages/send:
   *   post:
   *     summary: Send an email message
   *     description: |
   *       Sends a finalized message. This should be used after confirming or editing a generated draft.
   *     tags:
   *       - LLM Tools
   *     requestBody:
   *       required: true
   *       content:
   *         application/json:
   *           schema:
   *             $ref: '#/components/schemas/SendMessage'
   *     responses:
   *       201:
   *         description: Message sent
   *         content:
   *           application/json:
   *             schema:
   *               type: object
   *               properties:
   *                 status:
   *                   type: string
   *                   example: "sent"
   */
  app.post('/messages/send', (req, res) => {
    const { recipient, message } = req.body;
    res.status(201).json({ status: 'sent', to: recipient });
  });
  