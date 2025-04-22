/**
 * @openapi
 * /calendar/meetings:
 *   post:
 *     summary: Book a new meeting
 *     description: |
 *       Books a meeting with one or more participants. Ideal for use by AI agents or assistants in productivity workflows.
 *     tags:
 *       - LLM Tools
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/NewMeetingRequest'
 *     responses:
 *       201:
 *         description: Meeting booked successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/MeetingConfirmation'
 *       400:
 *         description: Invalid request data
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 */
app.post('/calendar/meetings', (req, res) => {
    const { title, participants, startTime, durationMinutes } = req.body;
  
    if (!title || !participants?.length || !startTime || !durationMinutes) {
      return res.status(400).json({
        error: 'INVALID_INPUT',
        message: 'Missing required fields'
      });
    }
  
    res.status(201).json({
      meetingId: 712,
      status: 'confirmed',
      startTime,
      durationMinutes,
      participants
    });
  });
  