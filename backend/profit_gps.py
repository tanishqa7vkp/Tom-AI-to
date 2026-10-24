
from pydantic import BaseModel, Field
from typing import Literal


class FarmConditions(BaseModel):
    crop: str
    temperature_c: float
    humidity_percent: float = Field(ge=0, le=100)
    rainfall_mm: float = Field(ge=0)
    area_acres: float = Field(gt=0)


def calculate_profit_gps(data: FarmConditions):
    recommendations = []

    if data.humidity_percent >= 80 and data.rainfall_mm >= 10:
        recommendations.append({
            "action": "Inspect your crop for signs of fungal disease today.",
            "reason": "High humidity and rainfall can increase fungal disease risk.",
            "priority": "HIGH",
            "score": 90
        })

    if data.temperature_c >= 35:
        recommendations.append({
            "action": "Check soil moisture and consider irrigation if needed.",
            "reason": "High temperatures can increase crop water stress.",
            "priority": "HIGH",
            "score": 85
        })

    if data.rainfall_mm >= 40:
        recommendations.append({
            "action": "Inspect drainage and check for standing water.",
            "reason": "Heavy rainfall can cause waterlogging.",
            "priority": "HIGH",
            "score": 88
        })

    if not recommendations:
        recommendations.append({
            "action": "Inspect your crop and monitor soil moisture today.",
            "reason": "No major weather-based warning was triggered.",
            "priority": "LOW",
            "score": 30
        })

    recommendations.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return {
        "crop": data.crop,
        "top_action": recommendations[0],
        "other_actions": recommendations[1:],
        "note": "Initial weather-rule recommendations; not a validated financial forecast."
    }
