import express from "express";
import dotenv from "dotenv";
dotenv.config();
const app = express();
const PORT = process.env.POSTGRESS_SQL_URL || 3000;
app.use(express.json());
// Ruta base
app.get("/", (req, res) => {
    res.send("Servidor Express con TypeScript funcionando 🚀");
});
// Iniciar servidor
app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
});
