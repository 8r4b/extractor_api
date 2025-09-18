import os
import httpx
import json
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
import auth # Import your auth module to get the current user

router = APIRouter()

@router.post("/paddle/webhook/")
async def paddle_webhook(request: Request, db: Session = Depends(get_db)):
    """Handles incoming webhooks from Paddle to update subscription status."""
    data = await request.form()
    # In a real app, you'd verify the webhook signature here
    event_type = data.get("event_type")
    
    if event_type == "subscription.created" or event_type == "subscription.updated":
        email = data.get("data[customer][email]")
        status = data.get("data[status]") # e.g., "active", "past_due"
        
        user = db.query(User).filter(User.email == email).first()
        if user and status:
            user.subscription_status = status
            db.commit()
            return {"status": "success"}
            
    return {"status": "ignored"}


@router.get("/checkout")
async def get_checkout_url(current_user: User = Depends(auth.get_current_user)):
    """
    Creates a checkout session via the Paddle API for the logged-in user.
    """
    api_key = os.getenv("PADDLE_API_KEY")
    price_id = os.getenv("PADDLE_PRICE_ID")

    # Add this line for debugging
    print(f"DEBUG: Using Paddle API Key: '{api_key}'")

    if not api_key or not price_id:
        raise HTTPException(status_code=500, detail="Paddle API Key or Price ID is not configured.")

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
    }
    payload = {
        "items": [{"price_id": price_id, "quantity": 1}],
        "customer": {"email": current_user.email},
        "custom_data": { "user_id": str(current_user.id) }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://sandbox-api.paddle.com/transactions", headers=headers, json=payload)

            if response.status_code == 201:
                checkout_url = response.json().get("data", {}).get("checkout", {}).get("url")
                if not checkout_url:
                     raise HTTPException(status_code=500, detail="Could not retrieve checkout URL from payment provider.")
                return {"checkout_url": checkout_url}
            else:
                error_details = response.json()
                error_message = error_details.get('error', {}).get('detail', 'Unknown Paddle error')
                print(f"PADDLE API FAILED: Status: {response.status_code}, Details: {json.dumps(error_details, indent=2)}")
                raise HTTPException(status_code=500, detail=f"Paddle Error: {error_message}")

    except httpx.RequestError as e:
        print(f"Could not connect to Paddle API. Error: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to payment provider.")