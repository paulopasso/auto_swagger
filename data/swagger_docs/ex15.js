/**
 * @openapi
 * /products/recommendations:
 *   get:
 *     summary: Get product recommendations
 *     description: |
 *       Returns a list of recommended products based on user's browsing history, preferences, and optionally filtered by a price range.
 *       The recommendations are automatically ranked and limited by the provided `limit` parameter.
 *     tags:
 *       - Products
 *     parameters:
 *       - in: query
 *         name: minPrice
 *         required: false
 *         schema:
 *           type: number
 *           minimum: 0
 *           default: 0
 *         description: Minimum price for recommended products
 *       - in: query
 *         name: maxPrice
 *         required: false
 *         schema:
 *           type: number
 *           minimum: 1
 *           default: 500
 *         description: Maximum price for recommended products
 *       - in: query
 *         name: limit
 *         required: false
 *         schema:
 *           type: integer
 *           minimum: 1
 *           maximum: 100
 *           default: 10
 *         description: Maximum number of products to return (1–100)
 *     responses:
 *       200:
 *         description: List of recommended products
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Product'
 */
app.get('/products/recommendations', (req, res) => {
    const limit = Math.min(parseInt(req.query.limit) || 10, 100);
  
    const mockProducts = Array.from({ length: limit }, (_, i) => ({
      id: i + 1,
      name: `Recommended Product ${i + 1}`,
      price: 50 + i,
      inStock: true
    }));
  
    res.json(mockProducts);
  });
  