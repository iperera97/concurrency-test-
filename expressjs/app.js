const express = require('express');
const { Pool } = require('pg');
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');
const dotenv = require('dotenv');
const winston = require('winston');

dotenv.config();

const app = express();
const port = 8000;

const pool = new Pool({
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT,
});

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console(),
  ],
});

app.use(express.json());

app.post('/sync-users', async (req, res) => {
  const start_time = Date.now();

  try {
    const timestamp_ns = process.hrtime.bigint();
    const unique_id = uuidv4();
    const username = `user_${timestamp_ns}_${unique_id}`;
    const email = `${username}@example.com`;
    const password = crypto.randomBytes(8).toString('hex');

    const client = await pool.connect();

    try {
      const result = await client.query(
        `INSERT INTO auth_user (
          username, 
          email, 
          password, 
          is_superuser, 
          is_staff, 
          is_active, 
          date_joined,
          first_name,
          last_name
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) RETURNING id`,
        [
          username, 
          email, 
          password, 
          false,  // is_superuser
          false,  // is_staff
          true,   // is_active
          new Date(),  // date_joined
          '', // first_name
          ''  // last_name
        ]
      );

      const userId = result.rows[0].id;
      res.status(201).json({ id: userId });
      logger.info(`User created with ID: ${userId}`);
    } finally {
      client.release();
    }
  } catch (err) {
    res.status(400).json({ error: `${err.message}` });
    logger.error(`Error creating user: ${err.message}`);
  }

  const execution_time = (Date.now() - start_time) / 1000;
  logger.info(`POST /sync-user execution time: ${execution_time.toFixed(4)} seconds`);
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
