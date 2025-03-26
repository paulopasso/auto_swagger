/**
 * @openapi
 * /products/{id}:
 *   put:
 *     summary: Update a product
 *     description: Update the details of an existing product by its ID.
 *     tags:
 *       - Products
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: The ID of the product to update
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/UpdateProduct'
 *     responses:
 *       204:
 *         description: Product updated successfully
 *       404:
 *         description: Product not found
 */
app.put('/products/:id', (req, res) => {
    const id = parseInt(req.params.id);
    // Fake DB update logic
    if (id < 1000) {
      // Assume update happens here
      res.status(204).send();
    } else {
      res.status(404).send({ message: 'Product not found' });
    }
  });
  