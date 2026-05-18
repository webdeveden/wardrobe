import axios from "axios";
import { authToken } from "../stores/auth";

/**
 * @typedef {import("../types.js").Category} Category
 * @typedef {import("../types.js").Era} Era
 * @typedef {import("../types.js").Product} Product
 * @typedef {import("../types.js").ProductListResponse} ProductListResponse
 * @typedef {import("../types.js").ChatResponse} ChatResponse
 *
 * @typedef {{ page?: number, pageSize?: number, search?: string, category?: string, era?: string, sort?: string }} CatalogQuery
 * @typedef {{ name: string, description: string, aisle: string, quantity: number, categorySlug: string, eraSlug: string, images: Array<{ url: string, alt?: string, sortOrder?: number }> }} ProductInput
 * @typedef {{ token: string, user: { id: number, email: string, role: "USER" | "ADMIN" } }} AuthResponse
 */

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:4000/api",
});

api.interceptors.request.use((config) => {
  const token = authToken.value;
  if (token && config.url?.startsWith("/admin")) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/** @returns {Promise<{ categories: Category[], eras: Era[] }>} */
export async function getMeta() {
  const { data } = await api.get("/catalog/meta");
  return data;
}

/**
 * @param {CatalogQuery} query
 * @returns {Promise<ProductListResponse>}
 */
export async function getProducts(query) {
  const { data } = await api.get("/catalog/products", { params: query });
  return data;
}

/**
 * @param {string} slug
 * @returns {Promise<Product>}
 */
export async function getProduct(slug) {
  const { data } = await api.get(`/catalog/products/${slug}`);
  return data;
}

/** @returns {Promise<Product[]>} */
export async function getAdminProducts() {
  const { data } = await api.get("/admin/products");
  return data;
}

/**
 * @param {ProductInput} payload
 * @returns {Promise<Product>}
 */
export async function createProduct(payload) {
  const { data } = await api.post("/admin/products", payload);
  return data;
}

/**
 * @param {File[]} files
 * @returns {Promise<Array<{ url: string, originalName: string }>>}
 */
export async function uploadProductImages(files) {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }

  const { data } = await api.post("/admin/uploads", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return data.files;
}

/**
 * @param {number} id
 * @param {ProductInput} payload
 * @returns {Promise<Product>}
 */
export async function updateProduct(id, payload) {
  const { data } = await api.put(`/admin/products/${id}`, payload);
  return data;
}

/** @param {number} id */
export async function deleteProduct(id) {
  await api.delete(`/admin/products/${id}`);
}

/**
 * @param {string} message
 * @returns {Promise<ChatResponse>}
 */
export async function sendChatMessage(message) {
  const { data } = await api.post("/chat/message", { message });
  return data;
}

/** @returns {Promise<AuthResponse>} */
export async function fetchMe() {
  const { data } = await api.get("/auth/me", {
    headers: { Authorization: `Bearer ${authToken.value}` },
  });
  return data;
}

/**
 * @param {string} email
 * @param {string} password
 * @returns {Promise<AuthResponse>}
 */
export async function login(email, password) {
  const { data } = await api.post("/auth/login", { email, password });
  return data;
}

/**
 * @param {string} email
 * @param {string} password
 * @returns {Promise<AuthResponse>}
 */
export async function register(email, password) {
  const { data } = await api.post("/auth/register", { email, password });
  return data;
}
