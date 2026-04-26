from datetime import datetime, timedelta
from typing import Optional


from sqlalchemy.orm import Session

from . import models, schemas, keygen


def get_db_url_by_key(db: Session, url_key: str):
    return (
        db.query(models.URL)
        .filter(models.URL.key == url_key, models.URL.is_active)
        .first()
    )


def get_active_non_expired_url(db: Session, url_key: str):
    db_url = get_db_url_by_key(db, url_key)

    if not db_url:
        return None

    if db_url.expires_at and db_url.expires_at < datetime.utcnow():
        db.delete(db_url)
        db.commit()
        return None

    return db_url


def create_unique_random_key(db: Session):
    key = keygen.create_random_key()

    while get_db_url_by_key(db, key):
        key = keygen.create_random_key()

    return key


def create_db_url(db: Session, url: schemas.URLBase):
    key = create_unique_random_key(db)
    secret_key = f"{key}_{keygen.create_random_key(length=8)}"

    expires_at = url.expires_at or datetime.utcnow() + timedelta(days=7)

    db_url = models.URL(
        target_url=url.target_url,
        key=key,
        secret_key=secret_key,
        expires_at=expires_at,
    )

    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    return db_url

def get_db_url_by_secret_key(db: Session, secret_key: str):
    return (
        db.query(models.URL)
        .filter(models.URL.secret_key == secret_key, models.URL.is_active)
        .first()
    )


def update_db_clicks(db: Session, db_url: models.URL):
    db_url.clicks += 1
    db.commit()
    db.refresh(db_url)
    return db_url


def create_visit(
    db: Session,
    db_url: models.URL,
    ip_address: Optional[str],
    country: Optional[str],
    user_agent: Optional[str],
):
    visit = models.Visit(
        url_id=db_url.id,
        ip_address=ip_address,
        country=country,
        user_agent=user_agent,
    )

    db.add(visit)
    db.commit()
    db.refresh(visit)

    return visit


def get_visits_for_url(db: Session, db_url: models.URL):
    return (
        db.query(models.Visit)
        .filter(models.Visit.url_id == db_url.id)
        .order_by(models.Visit.visited_at.desc())
        .all()
    )


def deactivate_db_url_by_secret_key(db: Session, secret_key: str):
    db_url = get_db_url_by_secret_key(db, secret_key)

    if db_url:
        db_url.is_active = False
        db.commit()
        db.refresh(db_url)

    return db_url