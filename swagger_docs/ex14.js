/**
 * @openapi
 * /posts:
 *   get:
 *     summary: Get posts filtered by tags
 *     description: Retrieve a list of blog posts filtered by one or more tags.
 *     tags:
 *       - Posts
 *     parameters:
 *       - in: query
 *         name: tags
 *         required: false
 *         schema:
 *           type: array
 *           items:
 *             type: string
 *           style: form
 *           explode: true
 *         description: Tags to filter posts by (e.g. ?tags=tech&tags=ai)
 *     responses:
 *       200:
 *         description: Filtered posts
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Post'
 */
app.get('/posts', (req, res) => {
    const { tags } = req.query;
    const examplePosts = [
      { id: 1, title: 'AI Trends 2025', tags: ['ai', 'tech'] },
      { id: 2, title: 'Vue vs React', tags: ['frontend', 'js'] },
    ];
  
    // Just return the example data; no filtering logic for mock
    res.json(examplePosts);
  });
  