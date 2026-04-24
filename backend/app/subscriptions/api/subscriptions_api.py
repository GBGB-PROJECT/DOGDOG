from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.db import get_db

router = APIRouter(prefix="/api/v2/subscriptions", tags=["Subscriptions"])

# 
