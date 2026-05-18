import "dotenv/config"; // should be first import to load env vars before other imports,because other imports might rely on env vars
import { PrismaClient } from "./generated/prisma/index.js";
import { PrismaPg } from "@prisma/adapter-pg";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL ?? "",
  ssl: {
    rejectUnauthorized: false,
  },
});

export const prisma = new PrismaClient({
  adapter: new PrismaPg(pool),
});
