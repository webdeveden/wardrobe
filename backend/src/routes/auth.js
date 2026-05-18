import bcrypt from "bcryptjs";
import { Router } from "express";
import { z } from "zod";
import { prisma } from "../db.js";
import { signToken, requireAuth } from "../middleware/auth.js";

export const authRouter = Router();

const authBodySchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

// TODO: review — /me re-fetches the user's current role from the DB and re-issues a fresh token.
// Call this on app load so that role changes made directly in the DB (e.g. promoting to ADMIN)
// take effect without requiring the user to log out and back in.
authRouter.get("/me", requireAuth, async (req, res) => {
  const user = await prisma.user.findUnique({ where: { id: req.user.sub } });
  if (!user) {
    res.status(404).json({ message: "User not found" });
    return;
  }
  const token = signToken({ sub: user.id, email: user.email, role: user.role });
  res.json({ token, user: { id: user.id, email: user.email, role: user.role } });
});

authRouter.post("/register", async (req, res) => {
  const parsed = authBodySchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ message: "Invalid body", issues: parsed.error.issues });
    return;
  }

  const { email, password } = parsed.data;
  const existing = await prisma.user.findUnique({ where: { email } });
  if (existing) {
    res.status(409).json({ message: "Email already registered" });
    return;
  }

  const passwordHash = await bcrypt.hash(password, 12);
  const user = await prisma.user.create({ data: { email, passwordHash } });
  const token = signToken({ sub: user.id, email: user.email, role: user.role });
  res.status(201).json({ token, user: { id: user.id, email: user.email, role: user.role } });
});

authRouter.post("/login", async (req, res) => {
  const parsed = authBodySchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ message: "Invalid body", issues: parsed.error.issues });
    return;
  }

  const { email, password } = parsed.data;
  const user = await prisma.user.findUnique({ where: { email } });
  if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
    res.status(401).json({ message: "Invalid credentials" });
    return;
  }

  const token = signToken({ sub: user.id, email: user.email, role: user.role });
  res.json({ token, user: { id: user.id, email: user.email, role: user.role } });
});
