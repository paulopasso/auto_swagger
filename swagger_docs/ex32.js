/**
 * @openapi
 * /calendar/availability:
 *   post:
 *     summary: Suggest available meeting slots
 *     description: |
 *       Suggests a list of available meeting time slots based on requested duration and preferred time range.
 *       This endpoint is intended for use by LLM agents to let the user choose from structured options.
 *     tags:
 *       - LLM Tools
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/AvailabilityRequest'
 *     responses:
 *       200:
 *         description: Suggested time slots
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/TimeSlotSuggestions'
 *       400:
 *         description: Invalid request
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 */
app.post('/calendar/availability', (req, res) => {
    const { durationMinutes, preferredStart, preferredEnd } = req.body;
  
    if (!durationMinutes || !preferredStart || !preferredEnd) {
      return res.status(400).json({
        error: 'MISSING_FIELDS',
        message: 'All fields are required.'
      });
    }
  
    res.json({
      suggestions: [
        {
          label: "Option 1: Tomorrow at 9:00 AM",
          startTime: "2025-03-27T09:00:00Z",
          durationMinutes: 30
        },
        {
          label: "Option 2: Tomorrow at 2:30 PM",
          startTime: "2025-03-27T14:30:00Z",
          durationMinutes: 30
        }
      ]
    });
  });
  