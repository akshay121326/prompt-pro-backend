from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime
import uuid

class PromptBase(SQLModel):
    name: str = Field(index=True)
    description: Optional[str] = None
    tags: Optional[str] = None  # Comma-separated tags

class Prompt(PromptBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    active_version_id: Optional[int] = None
    
    versions: List["PromptVersion"] = Relationship(back_populates="prompt")

class PromptVersionBase(SQLModel):
    version_number: int
    template: str
    input_variables: Optional[str] = None # JSON string of variables
    model_config_json: Optional[str] = None # JSON string for model params (temp, top_k, etc.)

class PromptVersion(PromptVersionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prompt_id: int = Field(foreign_key="prompt.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    commit_message: Optional[str] = None
    
    prompt: Prompt = Relationship(back_populates="versions")

class PromptCreate(PromptBase):
    pass

class PromptRead(PromptBase):
    id: int
    created_at: datetime
    active_version_id: Optional[int] = None
    versions: List["PromptVersion"] = []

class PromptVersionCreate(PromptVersionBase):
    pass

class PromptVersionUpdate(SQLModel):
    template: Optional[str] = None
    input_variables: Optional[str] = None
    model_config_json: Optional[str] = None
    commit_message: Optional[str] = None

class PromptUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None

class PromptPaginatedRead(SQLModel):
    items: List[PromptRead]
    total: int
    page: int
    size: int
