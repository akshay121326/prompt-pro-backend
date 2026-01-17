from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from app.core.database import get_session
from app.models.prompt import (
    Prompt, PromptCreate, PromptRead, PromptVersion, PromptVersionCreate, 
    PromptUpdate, PromptPaginatedRead, PromptVersionUpdate
)
from app.core.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=PromptRead)
def create_prompt(
    prompt: PromptCreate, 
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    db_prompt = Prompt.from_orm(prompt)
    session.add(db_prompt)
    session.commit()
    session.refresh(db_prompt)
    return db_prompt

@router.get("/", response_model=PromptPaginatedRead)
def read_prompts(
    search: Optional[str] = None,
    sort_by: str = "created_at",
    order: str = "desc",
    skip: int = 0, 
    limit: int = 10, 
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    query = select(Prompt)
    
    if search:
        query = query.where(
            (Prompt.name.contains(search)) | (Prompt.description.contains(search))
        )
    
    # Sorting
    sort_column = getattr(Prompt, sort_by, Prompt.created_at)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
        
    # Count total
    from sqlmodel import func
    total_query = select(func.count()).select_from(query.alias("sub"))
    total = session.exec(total_query).one()
    
    # Pagination
    prompts = session.exec(query.offset(skip).limit(limit)).all()
    
    return {
        "items": prompts,
        "total": total,
        "page": (skip // limit) + 1,
        "size": limit
    }

@router.get("/{prompt_id}", response_model=PromptRead)
def read_prompt(
    prompt_id: int, 
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    prompt = session.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.patch("/{prompt_id}", response_model=PromptRead)
def update_prompt(
    prompt_id: int,
    prompt_update: PromptUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    db_prompt = session.get(Prompt, prompt_id)
    if not db_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    prompt_data = prompt_update.dict(exclude_unset=True)
    for key, value in prompt_data.items():
        setattr(db_prompt, key, value)
    
    session.add(db_prompt)
    session.commit()
    session.refresh(db_prompt)
    return db_prompt

@router.post("/{prompt_id}/versions", response_model=PromptVersion)
def create_prompt_version(
    prompt_id: int,
    version: PromptVersionCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    prompt = session.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    db_version = PromptVersion(**version.dict(), prompt_id=prompt_id)
    session.add(db_version)
    session.commit()
    session.refresh(db_version)
    
    # If this is the active version isn't set, set this one as active
    if not prompt.active_version_id:
        prompt.active_version_id = db_version.id
        session.add(prompt)
        session.commit()
        session.refresh(db_version)
        
    return db_version

@router.post("/{prompt_id}/versions/{version_id}/set-active", response_model=PromptRead)
def set_active_version(
    prompt_id: int,
    version_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    prompt = session.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    version = session.get(PromptVersion, version_id)
    if not version or version.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="Version not found")
    
    prompt.active_version_id = version_id
    session.add(prompt)
    session.commit()
    session.refresh(prompt)
    return prompt

@router.delete("/{prompt_id}/versions/{version_id}")
def delete_prompt_version(
    prompt_id: int,
    version_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    version = session.get(PromptVersion, version_id)
    if not version or version.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="Version not found")
    
    prompt = session.get(Prompt, prompt_id)
    if prompt.active_version_id == version_id:
        # Prevent deleting the active version unless it's the last one?
        # Or just unset it. Let's unset it for now.
        prompt.active_version_id = None
        session.add(prompt)
    
    session.delete(version)
    session.commit()
    return {"message": "Version deleted successfully"}

@router.patch("/{prompt_id}/versions/{version_id}", response_model=PromptVersion)
def patch_prompt_version(
    prompt_id: int,
    version_id: int,
    version_update: PromptVersionUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    version = session.get(PromptVersion, version_id)
    if not version or version.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="Version not found")
    
    update_data = version_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(version, key, value)
    
    session.add(version)
    session.commit()
    session.refresh(version)
    return version

@router.delete("/{prompt_id}")
def delete_prompt(
    prompt_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    prompt = session.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    session.delete(prompt)
    session.commit()
    return {"message": "Prompt deleted successfully"}
