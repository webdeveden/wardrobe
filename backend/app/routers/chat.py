from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.schemas import ChatIn, ChatOut
from app.services.chat import ChatGenerationError, generate_chat_response

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=ChatOut)
async def send_message(body: ChatIn) -> ChatOut | JSONResponse:
    """Send a message to the Priest chatbot and get a reply with product recommendations."""
    try:
        return await generate_chat_response(body.message)
    except ChatGenerationError as error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to process chat message", "message": str(error)},
        )
