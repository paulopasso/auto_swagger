/**
 * @openapi
 * /products/search:
 *   get:
 *     summary: Search products
 *     description: Retrieve a list of products filtered by category, in-stock status, or price range.
 *     tags:
 *       - Products
 *     parameters:
 *       - in: query
 *         name: category
 *         schema:
 *           type: string
 *         description: Filter by category (e.g. "electronics")
 *       - in: query
 *         name: inStock
 *         schema:
 *           type: boolean
 *         description: Filter by stock availability
 *       - in: query
 *         name: minPrice
 *         schema:
 *           type: number
 *         description: Minimum price
 *       - in: query
 *         name: maxPrice
 *         schema:
 *           type: number
 *         description: Maximum price
 *     responses:
 *       200:
 *         description: Filtered list of products
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Product'
 */
app.get('/products/search', (req, res) => {
    const { category, inStock, minPrice, maxPrice } = req.query;
  
    // Mock filter logic
    const products = [
      { id: 1, name: 'Wireless Mouse', category: 'electronics', price: 25.99, inStock: true },
      { id: 2, name: 'Standing Desk', category: 'furniture', price: 199.99, inStock: false },
    ];
  
    // Simulated filtering (not actually filtering for simplicity)
    res.json(products);
  });
  