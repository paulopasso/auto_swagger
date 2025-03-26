/**
 * @openapi
 * /orders:
 *   post:
 *     summary: Create an order with items
 *     description: Submit a new order that includes customer info and multiple product items.
 *     tags:
 *       - Orders
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/OrderRequest'
 *     responses:
 *       201:
 *         description: Order created successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/OrderResponse'
 */
app.post('/orders', (req, res) => {
    const { customer, items } = req.body;
    const orderId = Math.floor(Math.random() * 10000);
  
    res.status(201).json({
      id: orderId,
      customer,
      items
    });
  });
  