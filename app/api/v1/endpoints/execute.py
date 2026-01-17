from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.llm_service import LLMService
from app.core.auth import get_current_user

router = APIRouter()

from sqlmodel import Session
from app.core.database import get_session
from app.models.provider import LLMProvider

class ExecuteRequest(BaseModel):
    provider_id: Optional[int] = None
    model_provider: str # openai, gemini, ollama
    model_name: str
    prompt_text: str
    config: Optional[Dict[str, Any]] = {}

class ExecuteResponse(BaseModel):
    response: str

@router.post("/", response_model=ExecuteResponse)
async def execute_prompt(
    request: ExecuteRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    try:
        provider_config = {}
        if request.provider_id:
            provider = session.get(LLMProvider, request.provider_id)
            if provider:
                provider_config = {
                    "api_key": provider.api_key,
                    "base_url": provider.base_url
                }

        response_text = await LLMService.execute_prompt(
            request.model_provider,
            request.model_name,
            request.prompt_text,
            request.config,
            provider_config=provider_config
        )
        return ExecuteResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
