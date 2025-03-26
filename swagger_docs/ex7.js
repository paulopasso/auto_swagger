/**
 * @openapi
 * /products/{id}/image:
 *   post:
 *     summary: Upload product image
 *     description: Upload an image for a specific product.
 *     tags:
 *       - Products
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: The ID of the product to upload the image for
 *     requestBody:
 *       required: true
 *       content:
 *         multipart/form-data:
 *           schema:
 *             type: object
 *             properties:
 *               image:
 *                 type: string
 *                 format: binary
 *     responses:
 *       200:
 *         description: Image uploaded successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: "Image uploaded"
 *       400:
 *         description: Bad request (missing file)
 */
app.post('/products/:id/image', (req, res) => {
    // Assuming middleware like multer is used to handle file uploads
    if (!req.file) {
      return res.status(400).json({ message: 'Image file is required' });
    }
  
    res.json({ message: 'Image uploaded' });
  });
  