/**
 * @openapi
 * /products:
 *   post:
 *     summary: Create a new product
 *     description: Add a new product to the catalog.
 *     tags:
 *       - Products
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/NewProduct'
 *     responses:
 *       201:
 *         description: Product created successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Product'
 */
app.post('/products', (req, res) => {
    const product = {
      id: Math.floor(Math.random() * 10000),
      ...req.body
    };
    res.status(201).json(product);
  });
  