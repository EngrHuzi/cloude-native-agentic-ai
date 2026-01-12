"""
API route handlers
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from database import get_session
from models import Hero, HeroCreate, HeroRead, HeroUpdate


hero_router = APIRouter(prefix="/heroes", tags=["heroes"])


@hero_router.post("/", response_model=HeroRead)
def create_hero(hero: HeroCreate, session: Session = Depends(get_session)):
    """Create a new hero"""
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@hero_router.get("/", response_model=List[HeroRead])
def read_heroes(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    """Get all heroes with pagination"""
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes


@hero_router.get("/{hero_id}", response_model=HeroRead)
def read_hero(hero_id: int, session: Session = Depends(get_session)):
    """Get a specific hero by ID"""
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@hero_router.patch("/{hero_id}", response_model=HeroRead)
def update_hero(
    hero_id: int,
    hero: HeroUpdate,
    session: Session = Depends(get_session)
):
    """Update a hero"""
    db_hero = session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    hero_data = hero.model_dump(exclude_unset=True)
    for key, value in hero_data.items():
        setattr(db_hero, key, value)

    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@hero_router.delete("/{hero_id}")
def delete_hero(hero_id: int, session: Session = Depends(get_session)):
    """Delete a hero"""
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    session.delete(hero)
    session.commit()
    return {"message": "Hero deleted successfully"}
