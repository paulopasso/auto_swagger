/**
 * @openapi
 * /products/{id}:
 *   delete:
 *     summary: Delete a product
 *     description: Remove a product from the catalog using its ID.
 *     tags:
 *       - Products
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: The ID of the product to delete
 *     responses:
 *       204:
 *         description: Product deleted successfully
 *       404:
 *         description: Product not found
 */
app.delete('/products/:id', (req, res) => {
    const id = parseInt(req.params.id);
    if (id < 1000) {
      // Pretend deletion succeeded
      res.status(204).send();
    } else {
      res.status(404).json({ message: 'Product not found' });
    }
  });
  