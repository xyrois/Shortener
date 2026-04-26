import validators
import requests

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.datastructures import URL

from . import crud, models, schemas
from .config import get_settings
from .database import SessionLocal, engine
from datetime import datetime, timedelta

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="shortener_app/static"), name="static")


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)


def raise_not_found(request):
    raise HTTPException(
        status_code=404,
        detail=f"URL '{request.url}' doesn't exist or has expired",
    )


def get_admin_info(db_url: models.URL):
    base_url = URL(get_settings().base_url)

    db_url.url = str(base_url.replace(path=db_url.key))
    db_url.admin_url = str(base_url.replace(path=f"admin/{db_url.secret_key}"))

    return db_url

def get_country_from_ip(ip_address):
    if not ip_address or ip_address == "127.0.0.1":
        return "Localhost"

    try:
        response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=3)
        data = response.json()
        return data.get("country_name", "Unknown")
    except Exception:
        return "Unknown"
    
@app.get("/")
def frontend():
    return FileResponse("shortener_app/static/index.html")


@app.post("/url", response_model=schemas.URLInfo)
def create_url(url: schemas.URLBase, db: Session = Depends(get_db)):
    if not validators.url(url.target_url):
        raise_bad_request("Your provided URL is not valid")

    now = datetime.utcnow()
    max_expiration = now + timedelta(days=7)

    if url.expires_at:
        if url.expires_at < now:
            raise_bad_request("Expiration date cannot be in the past")

        if url.expires_at > max_expiration:
            raise_bad_request("Expiration date cannot be more than 7 days from now")

    db_url = crud.create_db_url(db=db, url=url)

    return get_admin_info(db_url)


@app.get("/admin/{secret_key}", response_model=schemas.URLAnalytics)
def get_url_info(
    secret_key: str,
    request: Request,
    db: Session = Depends(get_db),
):
    db_url = crud.get_db_url_by_secret_key(db, secret_key=secret_key)

    if not db_url:
        raise_not_found(request)

    url_info = get_admin_info(db_url)
    url_info.visits = crud.get_visits_for_url(db, db_url)

    return url_info


@app.delete("/admin/{secret_key}")
def delete_url(
    secret_key: str,
    request: Request,
    db: Session = Depends(get_db),
):
    db_url = crud.deactivate_db_url_by_secret_key(db, secret_key=secret_key)

    if db_url:
        return {"detail": f"Successfully deleted shortened URL for '{db_url.target_url}'"}

    raise_not_found(request)


@app.get("/{url_key}")
def forward_to_target_url(
    url_key: str,
    request: Request,
    db: Session = Depends(get_db),
):
    db_url = crud.get_active_non_expired_url(db=db, url_key=url_key)

    if db_url:
        ip_address = request.client.host if request.client else None
        country = get_country_from_ip(ip_address)

        crud.update_db_clicks(db=db, db_url=db_url)

        crud.create_visit(
            db=db,
            db_url=db_url,
            ip_address=ip_address,
            country=country,
            user_agent=request.headers.get("user-agent"),
        )

        return RedirectResponse(db_url.target_url)

    raise_not_found(request)