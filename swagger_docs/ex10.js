/**
 * @openapi
 * /orders:
 *   post:
 *     summary: Create a new order
 *     description: Submit a new order with a valid status and payment method.
 *     tags:
 *       - Orders
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/NewOrder'
 *     responses:
 *       201:
 *         description: Order successfully created
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Order'
 *       400:
 *         description: Invalid input
 */
app.post('/orders', (req, res) => {
    const { status, paymentMethod } = req.body;
    const validStatuses = ['pending', 'confirmed', 'shipped'];
    const validPayments = ['card', 'paypal'];
  
    if (!validStatuses.includes(status) || !validPayments.includes(paymentMethod)) {
      return res.status(400).json({ message: 'Invalid status or payment method' });
    }
  
    const order = {
      id: Math.floor(Math.random() * 1000),
      status,
      paymentMethod
    };
  
    res.status(201).json(order);
  });
  