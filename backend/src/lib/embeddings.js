import { OpenAI } from "openai";
import { prisma } from "../db.js";

/**
 * @typedef {{ productId: number, embedding: number[], text: string }} ProductEmbedding
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

/** @type {ProductEmbedding[] | null} */
let cachedEmbeddings = null;

/**
 * Generate embeddings for all products in the catalog.
 * Caches results in memory for the lifetime of the server.
 * @returns {Promise<ProductEmbedding[]>}
 */
export async function getProductEmbeddings() {
  if (cachedEmbeddings) {
    return cachedEmbeddings;
  }

  console.log("Generating product embeddings...");

  const products = await prisma.product.findMany({
    include: {
      category: true,
      era: true,
      images: {
        orderBy: { sortOrder: "asc" },
        take: 1,
      },
    },
  });

  /** @type {ProductEmbedding[]} */
  const embeddings = [];

  for (const product of products) {
    const text = `
Product: ${product.name}
Description: ${product.description}
Category: ${product.category.name}
Era: ${product.era.name}
Aisle: ${product.aisle}
Quantity: ${product.quantity}
    `.trim();

    try {
      const response = await openai.embeddings.create({
        model: "text-embedding-3-small",
        input: text,
      });

      embeddings.push({
        productId: product.id,
        embedding: response.data[0].embedding,
        text,
      });
    } catch (error) {
      console.error(`Failed to embed product ${product.id}:`, error);
    }
  }

  cachedEmbeddings = embeddings;
  console.log(`Generated embeddings for ${embeddings.length} products`);

  return embeddings;
}

/**
 * @param {number[]} a
 * @param {number[]} b
 * @returns {number}
 */
function cosineSimilarity(a, b) {
  const dotProduct = a.reduce((sum, val, i) => sum + val * b[i], 0);
  const magnitudeA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0));
  const magnitudeB = Math.sqrt(b.reduce((sum, val) => sum + val * val, 0));

  if (magnitudeA === 0 || magnitudeB === 0) return 0;
  return dotProduct / (magnitudeA * magnitudeB);
}

/**
 * Find the most relevant products for a user query using semantic search.
 * @param {string} userQuery
 * @param {number} [topK=5]
 * @returns {Promise<Array<{productId: number, similarity: number, product: any}>>}
 */
export async function findRelevantProducts(userQuery, topK = 5) {
  try {
    const queryResponse = await openai.embeddings.create({
      model: "text-embedding-3-small",
      input: userQuery,
    });

    const queryEmbedding = queryResponse.data[0].embedding;
    const productEmbeddings = await getProductEmbeddings();

    const similarities = productEmbeddings.map((pe) => ({
      productId: pe.productId,
      similarity: cosineSimilarity(queryEmbedding, pe.embedding),
    }));

    const topProducts = similarities
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, topK);

    const productIds = topProducts.map((p) => p.productId);
    const products = await prisma.product.findMany({
      where: { id: { in: productIds } },
      include: {
        category: true,
        era: true,
        images: { orderBy: { sortOrder: "asc" } },
      },
    });

    return topProducts
      .map((tp) => ({
        productId: tp.productId,
        similarity: tp.similarity,
        product: products.find((p) => p.id === tp.productId),
      }))
      .filter((item) => item.product !== undefined);
  } catch (error) {
    console.error("Error finding relevant products:", error);
    return [];
  }
}
