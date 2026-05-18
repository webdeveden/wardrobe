import express from "express";
import { z } from "zod";
import { generateChatResponse } from "../lib/chat.js";

export const chatRouter = express.Router();

const chatMessageSchema = z.object({
  message: z.string().min(1).max(1000),
});

/**
 * POST /api/chat/message
 * Send a message to the Priest chatbot and get a response with product recommendations
 */
chatRouter.post("/message", async (req, res) => {
  try {
    const parsed = chatMessageSchema.safeParse(req.body);

    if (!parsed.success) {
      return res.status(400).json({
        error: "Invalid request",
        details: parsed.error.issues,
      });
    }

    const { message } = parsed.data;
    const response = await generateChatResponse(message);

    res.json(response);
  } catch (error) {
    console.error("Chat endpoint error:", error);
    res.status(500).json({
      error: "Failed to process chat message",
      message: error instanceof Error ? error.message : "Unknown error occurred",
    });
  }
});
