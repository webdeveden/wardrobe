"""RAG chat: retrieve relevant products, then ask the LLM to answer with them as context."""

import logging

from app.config import settings
from app.schemas import ChatOut, RecommendedProduct
from app.services.embeddings import find_relevant_products
from app.services.llm import get_llm_client

logger = logging.getLogger(__name__)

FALLBACK_REPLY = "I'm sorry, I couldn't generate a response. Please try again."

GUIDELINES = """Guidelines:
- Be friendly and conversational
- Respond using Markdown: use **bold**, *italic*, bullet lists, etc. where it improves clarity
- When you mention a product from the catalog, always link it as [Product Name](/products/slug) using the slug provided in the context
- Only link products that are actually relevant to your answer — do not mention a product just to fill space
- If you don't have information about a product, be honest about it
- Keep responses concise but helpful (2-3 sentences typically)
- Always be enthusiastic about helping customers find what they need"""


class ChatGenerationError(RuntimeError):
    pass


async def generate_chat_response(user_message: str) -> ChatOut:
    try:
        relevant = await find_relevant_products(user_message, top_k=5)

        context = ""
        if relevant:
            context = "Here are some relevant products from our catalog:\n\n"
            for index, item in enumerate(relevant, start=1):
                p = item.product
                context += (
                    f"{index}. {p.name} (slug: {p.slug}, Aisle: {p.aisle})\n"
                    f"   Category: {p.category.name}\n"
                    f"   Era: {p.era.name}\n"
                    f"   Description: {p.description}\n"
                    f"   In Stock: {'Yes' if p.quantity > 0 else 'No'}\n"
                    f"   Similarity Score: {item.similarity * 100:.1f}%\n\n"
                )

        recommended = [
            RecommendedProduct(id=item.product.id, name=item.product.name, slug=item.product.slug)
            for item in relevant[:3]
        ]

        system_prompt = (
            'You are "Priest", a helpful and friendly AI assistant for a wardrobe/clothing catalog.\n'
            "Your role is to help customers find products, answer questions about our inventory, "
            "and provide styling suggestions.\n\n"
            f"{f'Context:{chr(10)}{context}' if context else ''}\n\n"
            f"{GUIDELINES}"
        )

        response = await get_llm_client().chat.completions.create(
            model=settings.chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        reply = response.choices[0].message.content or FALLBACK_REPLY
        return ChatOut(reply=reply, recommended_products=recommended)
    except Exception as error:
        logger.exception("Error generating chat response")
        raise ChatGenerationError("Failed to generate chat response") from error
