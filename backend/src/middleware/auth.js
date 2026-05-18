import jwt from "jsonwebtoken";

const JWT_SECRET = process.env.JWT_SECRET ?? "dev-secret-change-me";

/**
 * @typedef {{ sub: number, email: string, role: "USER" | "ADMIN" }} AuthPayload
 */

/**
 * @param {import("express").Request} req
 * @param {import("express").Response} res
 * @returns {AuthPayload | null}
 */
function getAuthPayload(req, res) {
  const header = req.headers.authorization;
  if (!header?.startsWith("Bearer ")) {
    res.status(401).json({ message: "Unauthorized" });
    return null;
  }

  const token = header.slice(7);
  try {
    return /** @type {AuthPayload} */ (jwt.verify(token, JWT_SECRET, { algorithms: ["HS256"] }));
  } catch {
    res.status(401).json({ message: "Invalid token" });
    return null;
  }
}

/**
 * @param {import("express").Request} req
 * @param {import("express").Response} res
 * @param {import("express").NextFunction} next
 */
export function requireAuth(req, res, next) {
  const payload = getAuthPayload(req, res);
  if (!payload) return;

  req.user = payload;
  next();
}

/**
 * @param {import("express").Request} req
 * @param {import("express").Response} res
 * @param {import("express").NextFunction} next
 */
export function requireAdmin(req, res, next) {
  const payload = getAuthPayload(req, res);
  if (!payload) return;

  if (payload.role !== "ADMIN") {
    res.status(403).json({ message: "Forbidden" });
    return;
  }

  req.user = payload;
  next();
}

/**
 * @param {AuthPayload} payload
 * @returns {string}
 */
export function signToken(payload) {
  return jwt.sign(payload, JWT_SECRET, { algorithm: "HS256", expiresIn: "7d" });
}
