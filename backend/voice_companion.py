
from typing import Literal

from pydantic import BaseModel, Field


class VoiceRequest(BaseModel):
    question: str = Field(min_length=1)
    language: Literal["en", "hi", "mr"] = "en"


MESSAGES = {
    "en": {
        "greeting": "Hello! I am AGRIQ, your farming companion. How can I help?",
        "weather": "Check the AI Profit GPS for today's weather-related crop risks and recommended actions.",
        "price": "Use Bargaining Shield to compare buyer offers after transport costs and deductions.",
        "disease": "Inspect the affected leaves and stems. Avoid applying chemicals until the problem is identified.",
        "water": "Check soil moisture near the roots before watering. Avoid unnecessary irrigation.",
        "fallback": "I can help with crop health, watering, weather risks, and buyer offers. Please tell me what you need.",
    },
    "hi": {
        "greeting": "नमस्ते! मैं AGRIQ हूँ, आपका खेती साथी। बताइए, कैसे मदद करूँ?",
        "weather": "आज के मौसम से फसल को होने वाले जोखिम जानने के लिए AI Profit GPS देखें।",
        "price": "खरीदारों के प्रस्ताव की तुलना करने के लिए Bargaining Shield इस्तेमाल करें।",
        "disease": "प्रभावित पत्तियों और तनों की जाँच करें। समस्या पहचाने बिना रसायन न डालें।",
        "water": "सिंचाई से पहले जड़ों के पास मिट्टी की नमी जाँचें। अनावश्यक पानी देने से बचें।",
        "fallback": "मैं फसल, पानी, मौसम और खरीदारों के प्रस्ताव में मदद कर सकता हूँ। अपना सवाल बताइए।",
    },
    "mr": {
        "greeting": "नमस्कार! मी AGRIQ, तुमचा शेती साथी आहे. सांगा, कशी मदत करू?",
        "weather": "आजच्या हवामानामुळे पिकाला असलेले धोके जाणून घेण्यासाठी AI Profit GPS पाहा.",
        "price": "खरेदीदारांच्या ऑफरची तुलना करण्यासाठी Bargaining Shield वापरा.",
        "disease": "बाधित पाने आणि खोड तपासा. समस्या ओळखल्याशिवाय रसायने वापरू नका.",
        "water": "पाणी देण्यापूर्वी मुळांजवळील मातीतील ओलावा तपासा. अनावश्यक सिंचन टाळा.",
        "fallback": "मी पीक, पाणी, हवामान आणि खरेदीदारांच्या ऑफरबाबत मदत करू शकतो. तुमचा प्रश्न सांगा.",
    },
}


KEYWORDS = {
    "greeting": ["hello", "hi", "namaste", "नमस्ते", "नमस्कार"],
    "weather": ["weather", "rain", "temperature", "मौसम", "बारिश", "हवामान", "पाऊस"],
    "price": ["price", "buyer", "sell", "profit", "दाम", "कीमत", "खरीदार", "भाव", "दर", "विक्री"],
    "disease": ["disease", "yellow", "spots", "कीट", "बीमारी", "रोग", "डाग", "पिवळी"],
    "water": ["water", "irrigation", "watering", "पानी", "सिंचाई", "पाणी", "सिंचन"],
}


def respond_to_farmer(data: VoiceRequest):
    question = data.question.strip().lower()

    intent = "fallback"

    for category, words in KEYWORDS.items():
        if any(word in question for word in words):
            intent = category
            break

    response = MESSAGES[data.language][intent]

    return {
        "question": data.question,
        "language": data.language,
        "detected_intent": intent,
        "response_text": response,
        "speech_language": {
            "en": "en-IN",
            "hi": "hi-IN",
            "mr": "mr-IN",
        }[data.language],
        "note": "Prototype: keyword-based responses. Speech recognition and audio playback will be connected separately.",
    }
