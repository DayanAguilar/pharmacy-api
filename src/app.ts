
import express, { Request, Response, NextFunction } from "express";
import cors from "cors";
import { Pool } from "pg";
import dotenv from "dotenv";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());


const pool = new Pool({
  connectionString: process.env.POSTGRESS_SQL_URL,
});


async function getConnection(req: Request, res: Response, next: NextFunction) {
  try {
    const client = await pool.connect();
    (req as any).db = client;
    await client.query("BEGIN");
    res.on("finish", async () => {
      try {
        await client.query("COMMIT");
      } catch (err) {
        console.error("Commit error:", err);
      } finally {
        client.release();
      }
    });
    next();
  } catch (err) {
    console.error("DB connection error:", err);
    res.status(500).json({ error: "Database connection error" });
  }
}


app.get("/health", async (req: Request, res: Response) => {
  try {
    const client = await pool.connect();
    await client.query("SELECT 1");
    client.release();
    res.json({ status: "healthy", database: "connected" });
  } catch (err) {
    res.status(503).json({ status: "unhealthy", error: err });
  }
});


app.get("/products", getConnection, async (req: Request, res: Response) => {
  const client = (req as any).db;
  try {
    const result = await client.query(`
      SELECT category, product, laboratory, buy_price, sell_price, stock, expire_date, alert_date, product_id
      FROM products
    `);
    res.json(result.rows);
  } catch (err) {
    await client.query("ROLLBACK");
    console.error(err);
    res.status(500).json({ error: "Error fetching products" });
  }
});


app.post("/products", getConnection, async (req: Request, res: Response) => {
  const client = (req as any).db;
  const { category, product, laboratory, buy_price, sell_price, stock, expire_date, alert_date } = req.body;
  try {
    const result = await client.query(
      `INSERT INTO products (category, product, laboratory, buy_price, sell_price, stock, expire_date, alert_date)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8) RETURNING product_id`,
      [category, product, laboratory, buy_price, sell_price, stock, expire_date, alert_date]
    );
    res.json({ product_id: result.rows[0].product_id, ...req.body });
  } catch (err) {
    await client.query("ROLLBACK");
    console.error(err);
    res.status(500).json({ error: "Error creating product" });
  }
});


app.put("/products/:product_id", getConnection, async (req: Request, res: Response) => {
  const client = (req as any).db;
  const { product_id } = req.params;
  const { category, product, laboratory, buy_price, sell_price, stock, expire_date, alert_date } = req.body;
  try {
    const result = await client.query(
      `UPDATE products SET category=$1, product=$2, laboratory=$3, buy_price=$4, sell_price=$5, stock=$6, expire_date=$7, alert_date=$8
       WHERE product_id=$9`,
      [category, product, laboratory, buy_price, sell_price, stock, expire_date, alert_date, product_id]
    );
    if (result.rowCount === 0) return res.status(404).json({ error: "Product not found" });
    res.json({ product_id: Number(product_id), ...req.body });
  } catch (err) {
    await client.query("ROLLBACK");
    console.error(err);
    res.status(500).json({ error: "Error updating product" });
  }
});


app.delete("/products/:product_id", getConnection, async (req: Request, res: Response) => {
  const client = (req as any).db;
  const { product_id } = req.params;
  try {
    const result = await client.query(`DELETE FROM products WHERE product_id=$1`, [product_id]);
    if (result.rowCount === 0) return res.status(404).json({ error: "Product not found" });
    res.json({ message: "Product deleted successfully" });
  } catch (err) {
    await client.query("ROLLBACK");
    console.error(err);
    res.status(500).json({ error: "Error deleting product" });
  }
});

app.post("/sells", getConnection, async (req: Request, res: Response) => {
  const client = (req as any).db;
  const { product_id, quantity } = req.body;

  try {
   
    const stockResult = await client.query(
      `SELECT stock, product, sell_price FROM products WHERE product_id=$1`,
      [product_id]
    );

    if (stockResult.rowCount === 0) {
      await client.query("ROLLBACK");
      return res.status(404).json({ error: "Product not found" });
    }

    const { stock: current_stock, product, sell_price } = stockResult.rows[0];

    if (quantity > current_stock) {
      await client.query("ROLLBACK");
      return res.status(400).json({
        error: `Not enough stock. Available: ${current_stock}, Requested: ${quantity}`,
      });
    }

    
    const total_price = sell_price * quantity;

    
    const sellResult = await client.query(
      `INSERT INTO sells (product_id, date, quantity, total_price, product)
       VALUES ($1, NOW(), $2, $3, $4)
       RETURNING id, date`,
      [product_id, quantity, total_price, product]
    );

    
    await client.query(
      `UPDATE products SET stock = stock - $1 WHERE product_id=$2`,
      [quantity, product_id]
    );

    res.json({
      product_id,
      quantity,
      sell_id: sellResult.rows[0].id,
      date: sellResult.rows[0].date,
      total_price,
      product,
    });
  } catch (err) {
    await client.query("ROLLBACK");
    console.error(err);
    res.status(500).json({ error: "Error creating sell" });
  }
});

app.get("/sells/:date", getConnection, async (req: Request, res: Response) => {
  const client = (req as any).db;
  const { date } = req.params;
  
  try {
    const result = await client.query(
      `SELECT s.id, s.product_id, s.product, s.quantity, s.total_price, s.date 
       FROM sells s 
       WHERE s.date::date = $1::date
       ORDER BY s.id`,
      [date]
    );
    
    console.log(`Buscando ventas para fecha: ${date}`);
    console.log(`Resultados encontrados: ${result.rows.length}`);
    
    res.json(result.rows);
  } catch (err: any) {
    console.error('Error en query de ventas:', err);
    res.status(500).json({ error: "Error fetching sells", details: err.message || "Internal server error" });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
