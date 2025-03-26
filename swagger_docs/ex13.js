    /**
 * @openapi
 * /accounts/{id}:
 *   get:
 *     summary: Get account by ID
 *     description: Retrieve account details by account ID.
 *     tags:
 *       - Accounts
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: integer
 *         required: true
 *         description: The account ID
 *     responses:
 *       200:
 *         description: Account found
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Account'
 *       404:
 *         description: Account not found
 */
app.get('/accounts/:id', (req, res) => {
    const account = {
      id: parseInt(req.params.id),
      name: 'Ingvild',
      type: 'personal',
      status: 'active'
    };
  
    res.status(200).json(account);
  });
  
  /**
   * @openapi
   * /accounts/{id}:
   *   put:
   *     summary: Update account
   *     description: Update the name or status of an account.
   *     tags:
   *       - Accounts
   *     parameters:
   *       - in: path
   *         name: id
   *         schema:
   *           type: integer
   *         required: true
   *         description: The account ID
   *     requestBody:
   *       required: true
   *       content:
   *         application/json:
   *           schema:
   *             $ref: '#/components/schemas/UpdateAccount'
   *     responses:
   *       204:
   *         description: Account updated
   */
  app.put('/accounts/:id', (req, res) => {
    res.status(204).send();
  });
  
  /**
   * @openapi
   * /accounts/{id}:
   *   delete:
   *     summary: Delete account
   *     description: Delete an account by ID.
   *     tags:
   *       - Accounts
   *     parameters:
   *       - in: path
   *         name: id
   *         schema:
   *           type: integer
   *         required: true
   *         description: The account ID
   *     responses:
   *       204:
   *         description: Account deleted
   */
  app.delete('/accounts/:id', (req, res) => {
    res.status(204).send();
  });
  