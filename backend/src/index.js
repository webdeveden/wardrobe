import "dotenv/config";
import cors from "cors";
import express from "express";
import path from "node:path";
import { catalogRouter } from "./routes/catalog.js";
import { adminRouter } from "./routes/admin.js";
import { chatRouter } from "./routes/chat.js";
import { authRouter } from "./routes/auth.js";
import { getProductEmbeddings } from "./lib/embeddings.js";

const app = express();
const port = Number(process.env.PORT ?? 4000);

app.use(
  cors({
    origin: process.env.FRONTEND_ORIGIN ?? "http://localhost:5173",
  }),
);
app.use(express.json());
app.use("/uploads", express.static(path.resolve(process.cwd(), "uploads")));

app.get("/api/health", (_req, res) => {
  res.json({ ok: true });
});

app.use("/api/auth", authRouter);
app.use("/api/catalog", catalogRouter);
app.use("/api/admin", adminRouter);
app.use("/api/chat", chatRouter);

app.use((err, _req, res, _next) => {
  console.error(err);
  res.status(500).json({ message: "Internal server error" });
});

app.listen(port, async () => {
  console.log(`Backend listening on http://localhost:${port}`);

  try {
    await getProductEmbeddings();
  } catch (error) {
    console.error("Failed to initialize embeddings:", error);
  }
});
