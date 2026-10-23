
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Literal
import sqlite3

app = FastAPI(
    title="AGRIQ API",
    description="AI-powered farming decision platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = Path(__file__).resolve().parent / "farmers.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS farmers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                language TEXT NOT NULL,
                village TEXT NOT NULL,
                district TEXT NOT NULL,
                state TEXT NOT NULL,
                crop TEXT NOT NULL,
                soil_type TEXT NOT NULL,
                growth_stage TEXT NOT NULL,
                area_acres REAL NOT NULL,
                water_availability TEXT NOT NULL
            )
        """)


initialize_database()


class FarmerProfile(BaseModel):
    name: str = Field(min_length=1)
    language: Literal["English", "Hindi", "Marathi"]
    village: str
    district: str
    state: str
    crop: str
    soil_type: str
    growth_stage: str
    area_acres: float = Field(gt=0)
    water_availability: Literal["Low", "Medium", "High"]


@app.get("/")
def home():
    return {"message": "Welcome to AGRIQ API"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/api/farmers", status_code=201)
def create_farmer(profile: FarmerProfile):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO farmers (
                name, language, village, district, state,
                crop, soil_type, growth_stage, area_acres,
                water_availability
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            tuple(profile.model_dump().values())
        )
        farmer_id = cursor.lastrowid

    return {
        "message": "Farmer profile created successfully",
        "farmer_id": farmer_id
    }


@app.get("/api/farmers/{farmer_id}")
def get_farmer(farmer_id: int):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM farmers WHERE id = ?",
            (farmer_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Farmer not found")

    return dict(row)


@app.put("/api/farmers/{farmer_id}")
def update_farmer(farmer_id: int, profile: FarmerProfile):
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM farmers WHERE id = ?",
            (farmer_id,)
        ).fetchone()

        if existing is None:
            raise HTTPException(status_code=404, detail="Farmer not found")

        data = profile.model_dump()

        connection.execute(
            """
            UPDATE farmers SET
                name = ?,
                language = ?,
                village = ?,
                district = ?,
                state = ?,
                crop = ?,
                soil_type = ?,
                growth_stage = ?,
                area_acres = ?,
                water_availability = ?
            WHERE id = ?
            """,
            (*data.values(), farmer_id)
        )

    return {"message": "Farmer profile updated successfully"}
