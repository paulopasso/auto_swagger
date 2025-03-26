/**
 * @openapi
 * /products:
 *   get:
 *     summary: Get paginated list of products
 *     description: Retrieve a paginated list of products with metadata like total count and current page.
 *     tags:
 *       - Products
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           default: 1
 *         description: Page number
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 10
 *         description: Number of items per page
 *     responses:
 *       200:
 *         description: Paginated list of products
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/PaginatedProducts'
 */
app.get('/products', (req, res) => {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
  
    const products = Array.from({ length: limit }, (_, i) => ({
      id: (page - 1) * limit + i + 1,
      name: `Product ${(page - 1) * limit + i + 1}`,
      price: Math.floor(Math.random() * 100) + 1,
      inStock: true
    }));
  
    res.json({
      data: products,
      meta: {
        page,
        limit,
        total: 100,
        nextPage: page * limit < 100 ? page + 1 : null,
        prevPage: page > 1 ? page - 1 : null
      }
    });
  });
  