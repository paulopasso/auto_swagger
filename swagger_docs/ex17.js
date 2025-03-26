/**
 * @openapi
 * /support/tickets:
 *   post:
 *     summary: Create a support ticket
 *     description: |
 *       Submit a new support ticket. You can optionally include metadata like browser info or session ID.
 *       If input validation fails or a server error occurs, detailed error information will be returned.
 *     tags:
 *       - Support
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/NewSupportTicket'
 *     responses:
 *       201:
 *         description: Ticket successfully created
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/SupportTicket'
 *       400:
 *         description: Invalid request
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 *       500:
 *         description: Internal server error
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 */
app.post('/support/tickets', (req, res) => {
    const { title, message } = req.body;
  
    if (!title || !message) {
      return res.status(400).json({
        error: 'VALIDATION_ERROR',
        message: 'Title and message are required'
      });
    }
  
    const ticket = {
      id: Math.floor(Math.random() * 1000),
      title,
      status: 'open',
      createdAt: new Date().toISOString()
    };
  
    res.status(201).json(ticket);
  });
  