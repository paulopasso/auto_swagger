/**
 * @openapi
 * /weather:
 *   get:
 *     summary: Get current weather by city
 *     description: |
 *       Returns the current weather data for a specified city. Ideal for use by AI assistants or chatbots.
 *     tags:
 *       - LLM Tools
 *     parameters:
 *       - name: city
 *         in: query
 *         required: true
 *         schema:
 *           type: string
 *         description: Name of the city to get weather for
 *     responses:
 *       200:
 *         description: Current weather in the specified city
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/WeatherResponse'
 *       404:
 *         description: City not found
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 */
app.get('/weather', (req, res) => {
    const city = req.query.city;
    if (!city || city.toLowerCase() !== 'madrid') {
      return res.status(404).json({
        error: 'NOT_FOUND',
        message: `Weather for "${city}" not found`
      });
    }
  
    res.json({
      city: 'Madrid',
      temperatureCelsius: 22.5,
      condition: 'Sunny',
      humidity: 30,
      windKph: 15.2
    });
  });
  