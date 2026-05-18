import { OpenAI } from "openai";
import { findRelevantProducts } from "./embeddings.js";

/**
 * @typedef {{ reply: string, recommendedProducts: Array<{id: number, name: string, slug: string}> }} ChatResponse
 */

const customFetch = (input, init) => {
  const headers = new Headers(init?.headers);
  headers.set("Authorization", `Bearer ${process.env.OPENROUTER_API_KEY}`);
  return fetch(input, { ...init, headers });
};

const openai = new OpenAI({
  apiKey: process.env.OPENROUTER_API_KEY || "",
  baseURL: "https://openrouter.ai/api/v1",
  defaultHeaders: {
    "HTTP-Referer": "http://localhost:5173",
    "X-Title": "Wardrobe Catalog",
  },
  fetch: customFetch,
});

/**
 * Generate a chat response using RAG (Retrieval-Augmented Generation)
 * Finds relevant products and uses them as context for the AI response
 * @param {string} userMessage
 * @returns {Promise<ChatResponse>}
 */
export async function generateChatResponse(userMessage) {
  try {
    const relevantProducts = await findRelevantProducts(userMessage, 5);

    let productContext = "";
    /** @type {Array<{id: number, name: string, slug: string}>} */
    const recommendedProducts = [];

    if (relevantProducts.length > 0) {
      productContext = "Here are some relevant products from our catalog:\n\n";
      relevantProducts.forEach((item, index) => {
        const product = item.product;
        productContext += `${index + 1}. ${product.name} (slug: ${product.slug}, Aisle: ${product.aisle})
   Category: ${product.category.name}
   Era: ${product.era.name}
   Description: ${product.description}
   In Stock: ${product.quantity > 0 ? "Yes" : "No"}
   Similarity Score: ${(item.similarity * 100).toFixed(1)}%\n\n`;

        if (index < 3) {
          recommendedProducts.push({ id: product.id, name: product.name, slug: product.slug });
        }
      });
    }

    const systemPrompt = `You are "Priest", a helpful and friendly AI assistant for a wardrobe/clothing catalog.
Your role is to help customers find products, answer questions about our inventory, and provide styling suggestions.

${productContext ? `Context:\n${productContext}` : ""}

Guidelines:
- Be friendly and conversational
- Respond using Markdown: use **bold**, *italic*, bullet lists, etc. where it improves clarity
- When you mention a product from the catalog, always link it as [Product Name](/products/slug) using the slug provided in the context
- Only link products that are actually relevant to your answer — do not mention a product just to fill space
- If you don't have information about a product, be honest about it
- Keep responses concise but helpful (2-3 sentences typically)
- Always be enthusiastic about helping customers find what they need`;

    const response = await openai.chat.completions.create({
      model: "openai/gpt-4o-mini",
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userMessage },
      ],
      temperature: 0.7,
      max_tokens: 500,
    });

    const reply =
      response.choices[0].message.content ||
      "I'm sorry, I couldn't generate a response. Please try again.";

    return { reply, recommendedProducts };
  } catch (error) {
    console.error("Error generating chat response:", error);
    throw new Error("Failed to generate chat response");
  }
}
