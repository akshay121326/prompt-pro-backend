from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.core.database import get_session
from app.models.provider import LLMProvider, LLMProviderRead, LLMModel, LLMModelRead, LLMProviderUpdate, LLMModelUpdate
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[LLMProviderRead])
def read_providers(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    providers = session.exec(select(LLMProvider)).all()
    return providers

@router.post("/", response_model=LLMProviderRead)
def create_provider(
    provider: LLMProvider,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    session.add(provider)
    session.commit()
    session.refresh(provider)
    return provider

@router.delete("/{provider_id}")
def delete_provider(
    provider_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    provider = session.get(LLMProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    session.delete(provider)
    session.commit()
    return {"message": "Provider deleted successfully"}

@router.patch("/{provider_id}", response_model=LLMProviderRead)
def patch_provider(
    provider_id: int,
    provider_update: LLMProviderUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    db_provider = session.get(LLMProvider, provider_id)
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    update_data = provider_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_provider, key, value)
    
    session.add(db_provider)
    session.commit()
    session.refresh(db_provider)
    return db_provider

@router.post("/{provider_id}/models", response_model=LLMModelRead)
def create_model(
    provider_id: int,
    model: LLMModel,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    provider = session.get(LLMProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    model.provider_id = provider_id
    session.add(model)
    session.commit()
    session.refresh(model)
    return model

@router.delete("/{provider_id}/models/{model_id}")
def delete_model(
    provider_id: int,
    model_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    model = session.get(LLMModel, model_id)
    if not model or model.provider_id != provider_id:
        raise HTTPException(status_code=404, detail="Model not found")
    session.delete(model)
    session.commit()
    return {"message": "Model deleted successfully"}
