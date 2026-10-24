
from pydantic import BaseModel, Field
from typing import List


class BuyerOffer(BaseModel):
    buyer_name: str
    price_per_kg: float = Field(gt=0)
    transport_cost: float = Field(ge=0)
    other_deductions: float = Field(ge=0)


class BargainingRequest(BaseModel):
    crop: str
    quantity_kg: float = Field(gt=0)
    production_cost: float = Field(ge=0)
    offers: List[BuyerOffer] = Field(min_length=1)


def compare_buyer_offers(data: BargainingRequest):
    results = []

    for offer in data.offers:
        gross_revenue = data.quantity_kg * offer.price_per_kg

        total_deductions = (
            offer.transport_cost + offer.other_deductions
        )

        net_revenue = gross_revenue - total_deductions
        estimated_profit = net_revenue - data.production_cost

        results.append({
            "buyer_name": offer.buyer_name,
            "price_per_kg": offer.price_per_kg,
            "gross_revenue_inr": round(gross_revenue, 2),
            "total_deductions_inr": round(total_deductions, 2),
            "net_revenue_inr": round(net_revenue, 2),
            "estimated_profit_inr": round(estimated_profit, 2)
        })

    results.sort(
        key=lambda item: item["net_revenue_inr"],
        reverse=True
    )

    best_offer = results[0]

    return {
        "crop": data.crop,
        "quantity_kg": data.quantity_kg,
        "recommended_buyer": best_offer["buyer_name"],
        "best_offer": best_offer,
        "all_offers_ranked": results,
        "explanation": (
            f"{best_offer['buyer_name']} provides the highest "
            "net revenue after the entered deductions."
        ),
        "note": (
            "Comparison uses farmer-entered prices and costs. "
            "Payment reliability, quality differences and market "
            "prices have not yet been verified."
        )
    }
