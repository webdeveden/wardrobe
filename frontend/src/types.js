/**
 * @typedef {{ id: number, name: string, slug: string }} Category
 * @typedef {{ id: number, name: string, slug: string }} Era
 * @typedef {{ id: number, url: string, alt?: string | null, sortOrder: number }} ProductImage
 * @typedef {{ id: number, name: string, slug: string, description: string, aisle: string, quantity: number, createdAt: string, category: Category, era: Era, images: ProductImage[] }} Product
 * @typedef {{ items: Product[], total: number, page: number, pageSize: number, totalPages: number }} ProductListResponse
 * @typedef {{ id: number, name: string, slug: string }} RecommendedProduct
 * @typedef {{ id: string, role: "user" | "assistant", content: string, recommendedProducts?: RecommendedProduct[], timestamp: Date }} ChatMessage
 * @typedef {{ reply: string, recommendedProducts: RecommendedProduct[] }} ChatResponse
 */

export {};
