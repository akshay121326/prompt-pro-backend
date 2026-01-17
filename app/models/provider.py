from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime

class LLMProviderBase(SQLModel):
    name: str = Field(index=True)
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    is_active: bool = True

class LLMProvider(LLMProviderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    models: List["LLMModel"] = Relationship(
        back_populates="provider",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class LLMModelBase(SQLModel):
    name: str = Field(index=True)
    capabilities: Optional[str] = None # e.g., "chat, vision"

class LLMModel(LLMModelBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    provider_id: int = Field(foreign_key="llmprovider.id")
    
    provider: LLMProvider = Relationship(back_populates="models")

class LLMProviderUpdate(SQLModel):
    name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    is_active: Optional[bool] = None

class LLMModelUpdate(SQLModel):
    name: Optional[str] = None
    capabilities: Optional[str] = None

class LLMProviderRead(LLMProviderBase):
    id: int
    models: List["LLMModel"] = []

class LLMModelRead(LLMModelBase):
    id: int
    provider_id: int
