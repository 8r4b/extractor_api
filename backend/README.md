# Resume Extractor API

The Resume Extractor API is a powerful tool designed to parse resume files (`.pdf`, `.docx`, etc.), extract a comprehensive list of skills, and provide AI-generated feedback for improvement. It's built for developers who need to integrate resume analysis into their applications without handling the complexities of file parsing, AI prompt engineering, and payment systems.

This API is a paid service managed via Paddle, offering a simple, usage-based subscription model.

**Live API Docs:** [https://extractor-api-2m1a.onrender.com/docs](https://extractor-api-2m1a.onrender.com/docs)

---

## Features

- **Multi-Format Support:** Handles various resume file formats, including PDF, DOCX, and plain text.
- **AI-Powered Skill Extraction:** Leverages OpenAI's GPT models to intelligently identify and extract technical, soft, and domain-specific skills.
- **Constructive Feedback:** Provides AI-generated suggestions on how to improve the resume.
- **Secure and Scalable:** Built with FastAPI, featuring user authentication, rate limiting, and a production-ready architecture.
- **Simple Subscription:** Integrated with Paddle for easy and secure subscription management.

---

## Getting Started: The User Journey

To use the API, developers must follow this step-by-step journey.

### Step 1: Create an Account

First, you need to register for an account.

- **Endpoint:** `POST /api/signup`
- **Request Body:**
  ```json
  {
    "email": "your.email@example.com",
    "password": "YourStrongPassword123"
  }
  ```
- **Result:** A verification email will be sent to your address.

### Step 2: Verify Your Email

Click the verification link sent to your email. This will activate your account. Until you do this, you will not be able to log in or use the API.

### Step 3: Log In to Get an Access Token

Once your email is verified, you can log in to receive a JWT access token. This token must be included in the header of all subsequent authenticated requests.

- **Endpoint:** `POST /api/login`
- **Request Body (as form-data):**
  - `username`: `your.email@example.com`
  - `password`: `YourStrongPassword123`
- **Result:**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

### Step 4: Subscribe to a Plan

Your account is active, but you need a subscription to use the core features.

1.  **Get the Checkout Link:** Make an authenticated request to the checkout endpoint.
    - **Endpoint:** `GET /api/checkout`
    - **Header:** `Authorization: Bearer <your_access_token>`
2.  **Complete Payment:** The API will return a unique Paddle checkout URL. Open this URL in your browser and complete the payment process.
3.  **Activation:** Upon successful payment, Paddle will notify our server via a webhook, and your subscription will be automatically activated.

### Step 5: Use the API

You are now ready to analyze resumes!

- **Endpoint:** `POST /api/upload-resume/`
- **Header:** `Authorization: Bearer <your_access_token>`
- **Request Body (as multipart/form-data):**
  - `file`: Your resume file (`.pdf`, `.docx`, etc.).
- **Successful Response (200 OK):**
  ```json
  {
    "filename": "JohnDoe_Resume.pdf",
    "skills": [
      "Python",
      "FastAPI",
      "SQLAlchemy",
      "Project Management"
    ],
    "feedback": "This is a strong resume, but consider adding more quantifiable achievements..."
  }
  ```

---

## Python Example

Here is a complete Python script demonstrating how to use the API from start to finish.

```python
import requests
import json

# The base URL of the API
BASE_URL = "https://extractor-api-2m1a.onrender.com"

def login(email, password):
    """Logs in and returns an access token."""
    print("--- Logging in... ---")
    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            data={"username": email, "password": password}
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        access_token = response.json()['access_token']
        print("Login successful!")
        return access_token
    except requests.exceptions.HTTPError as e:
        print(f"Login Failed: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the API: {e}")
    return None

def upload_resume(token, file_path):
    """Uploads a resume file for analysis."""
    print("\n--- Uploading resume... ---")
    headers = {"Authorization": f"Bearer {token}"}
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f)}
        try:
            response = requests.post(
                f"{BASE_URL}/api/upload-resume/",
                headers=headers,
                files=files
            )
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                print("--- Analysis Result ---")
                print(json.dumps(response.json(), indent=2))
            else:
                print("--- Error ---")
                print(response.json())
        except requests.exceptions.RequestException as e:
            print(f"Error during upload: {e}")

if __name__ == "__main__":
    # Replace with your credentials
    USER_EMAIL = "your.email@example.com"
    USER_PASSWORD = "YourStrongPassword123"
    RESUME_FILE_PATH = "path/to/your/resume.pdf"

    # 1. Log in
    auth_token = login(USER_EMAIL, USER_PASSWORD)

    # 2. If login is successful, upload the resume
    if auth_token:
        upload_resume(auth_token, RESUME_FILE_PATH)
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of a request.

- **`200 OK`**: The request was successful.
- **`400 Bad Request`**: The request was malformed (e.g., invalid JSON, missing fields).
- **`401 Unauthorized`**: The access token is missing or invalid.
- **`402 Payment Required`**: The user does not have an active subscription.
- **`403 Forbidden`**: The user's email is not verified.
- **`429 Too Many Requests`**: The user has exceeded a rate limit.
- **`500 Internal Server Error`**: An unexpected error occurred on the server.

The response body for errors will typically contain a `detail` field with more information.
```json
{
  "detail": "Subscription inactive."
}
```
