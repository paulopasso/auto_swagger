/**
 * @openapi
 * /products/{id}:
 *   get:
 *     summary: Get product by ID
 *     description: Retrieve a single product using its unique ID.
 *     tags:
 *       - Products
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: The product ID
 *     responses:
 *       200:
 *         description: A single product
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Product'
 *       404:
 *         description: Product not found
 */
app.get('/products/:id', (req, res) => {
    const productId = parseInt(req.params.id);
    const product = {
      id: productId,
      name: 'Mechanical Keyboard',
      price: 79.99,
      inStock: true,
      tags: ['electronics', 'keyboards']
    };
  
    if (productId < 1000) {
      res.status(200).json(product);
    } else {
      res.status(404).send({ message: 'Product not found' });
    }
  });
  