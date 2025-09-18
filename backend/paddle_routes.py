import os
import logging
import httpx
import json
import hmac      # Add this import
import hashlib   # Add this import
from fastapi import APIRouter, Request, Depends, HTTPException
from schemas import SuccessResponse, ErrorResponse, DataResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User
import auth
from datetime import datetime  # Add this import

router = APIRouter()

# Set up logging
logger = logging.getLogger("paddle_routes")
logging.basicConfig(level=logging.INFO)

@router.post("/paddle/webhook/", response_model=SuccessResponse, responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}, tags=["Paddle"])
async def paddle_webhook(request: Request, db: Session = Depends(get_db)):
    """Handles and VERIFIES incoming JSON webhooks from Paddle."""
    
    # --- Start of Security Verification ---
    secret = os.getenv("PADDLE_WEBHOOK_SECRET")
    if not secret:
        logger.error("PADDLE_WEBHOOK_SECRET is not set on the server.")
        raise HTTPException(status_code=500, detail="Webhook secret not configured.")

    signature_header = request.headers.get("Paddle-Signature")
    if not signature_header:
        raise HTTPException(status_code=400, detail="Paddle-Signature header missing.")

    try:
        # Extract timestamp and signature from header
        parts = {key_value.split('=')[0]: key_value.split('=')[1] for key_value in signature_header.split(';')}
        timestamp = parts.get('ts')
        signature = parts.get('h1')

        # Get the raw request body as bytes
        raw_body = await request.body()

        # Create the signed payload string
        signed_payload = f"{timestamp}:{raw_body.decode('utf-8')}"

        # Compute the expected signature
        computed_signature = hmac.new(
            key=secret.encode('utf-8'),
            msg=signed_payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        # Compare signatures to verify the request is from Paddle
        if not hmac.compare_digest(computed_signature, signature):
            raise HTTPException(status_code=401, detail="Invalid webhook signature.")
            
    except Exception as e:
        logger.error(f"Webhook signature verification failed. Error: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature header format.")
    # --- End of Security Verification ---

    # If verification passes, process the payload (which we already have as raw_body)
    payload = json.loads(raw_body)
    event_type = payload.get("event_type")

    # The 'transaction.completed' event is the most reliable for new subscriptions
    if event_type == "transaction.completed":
        data = payload.get("data", {})
        user_id = data.get("custom_data", {}).get("user_id")
        is_subscription = any(item.get("price", {}).get("type") == "recurring" for item in data.get("items", []))
        
        if user_id and is_subscription and data.get("status") == "completed":
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                # If this is the first time they are becoming active, set the start date
                if user.subscription_status != "active":
                    user.subscription_start_date = datetime.utcnow() # Add this
                
                user.subscription_status = "active"
                user.api_calls_this_month = 0 # Also reset their count immediately on payment
                db.commit()
                logger.info(f"Activated subscription for user {user.email}")
                return SuccessResponse(message="Activated subscription.")

    # Handle cancellations
    if event_type == "subscription.canceled":
        data = payload.get("data", {})
        user_id = data.get("custom_data", {}).get("user_id")
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.subscription_status = "canceled"
            db.commit()
            logger.info(f"Canceled subscription for user {user.email}")
            return SuccessResponse(message="Subscription canceled.")

    logger.info(f"Ignored verified webhook event: {event_type}")
    return SuccessResponse(message=f"Ignored verified webhook event: {event_type}")

@router.get("/customer-portal", response_model=DataResponse, responses={500: {"model": ErrorResponse}, 503: {"model": ErrorResponse}}, tags=["Paddle"])
async def get_customer_portal(current_user: User = Depends(auth.get_current_user)):
    """
    Generates a Paddle customer portal link for the logged-in user.
    """
    api_key = os.getenv("PADDLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Paddle API Key is not configured.")

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
    }
    payload = {
        "customer": {"email": current_user.email}
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://sandbox-api.paddle.com/customers/login", headers=headers, json=payload)

            if response.status_code == 200:
                portal_url = response.json().get("data", {}).get("url")
                if not portal_url:
                    raise HTTPException(status_code=500, detail="Could not retrieve customer portal URL from payment provider.")
                return DataResponse(data={"customer_portal_url": portal_url})
            else:
                error_details = response.json()
                error_message = error_details.get('error', {}).get('detail', 'Unknown Paddle error')
                raise HTTPException(status_code=500, detail=f"Paddle Error: {error_message}")

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to payment provider.")

@router.get("/checkout", response_model=DataResponse, responses={500: {"model": ErrorResponse}, 503: {"model": ErrorResponse}}, tags=["Paddle"])
async def get_checkout_url(current_user: User = Depends(auth.get_current_user)):
    """
    Creates a checkout session via the Paddle API for the logged-in user.
    """
    api_key = os.getenv("PADDLE_API_KEY")
    price_id = os.getenv("PADDLE_PRICE_ID")

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
                return DataResponse(data={"checkout_url": checkout_url})
            else:
                error_details = response.json()
                error_message = error_details.get('error', {}).get('detail', 'Unknown Paddle error')
                raise HTTPException(status_code=500, detail=f"Paddle Error: {error_message}")

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to payment provider.")