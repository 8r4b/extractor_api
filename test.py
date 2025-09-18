import requests
import getpass
import os

# --- Configuration ---
# This is the URL where your API is running.
BASE_URL = "https://extractor-api-2m1a.onrender.com"

def login(email, password):
    """Logs in the user and returns an access token."""
    print("\n--- Step 1: Attempting to log in... ---")
    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            data={"username": email, "password": password}
        )
        if response.status_code == 200:
            access_token = response.json()['access_token']
            print("Login successful!")
            return access_token
        else:
            print(f"Login Failed. Status: {response.status_code}, Details: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the API: {e}")
        return None

def get_checkout_link(token):
    """Gets a subscription checkout link for the user."""
    print("\n--- Step 2: Fetching checkout link... ---")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/checkout", headers=headers)
    if response.status_code == 200:
        checkout_url = response.json()['checkout_url']
        print(f"Checkout URL received: {checkout_url}")
        return checkout_url
    else:
        print(f"Failed to get checkout link. Status: {response.status_code}, Details: {response.text}")
        return None

def upload_resume(token, file_path):
    """Uploads a resume file for analysis."""
    print("\n--- Step 3: Uploading resume for analysis... ---")
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return

    headers = {"Authorization": f"Bearer {token}"}
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        try:
            response = requests.post(
                f"{BASE_URL}/api/upload-resume/",
                headers=headers,
                files=files
            )
            print("\n--- Result ---")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to the API during upload: {e}")


if __name__ == "__main__":
    print("--- API Test Script ---")
    
    # Get user credentials
    test_email = input("Enter your test user email: ")
    test_password = getpass.getpass("Enter your test user password: ")

    # 1. Log in
    auth_token = login(test_email, test_password)

    if auth_token:

        get_checkout_link(auth_token)
        print("Please complete the payment in your browser before proceeding.")
        input("Press Enter to continue after payment...")

        # 3. Upload resume
        resume_file = "C:\\Users\\msi-pc\\Downloads\\Professional Modern CV Resume.pdf"
        upload_resume(auth_token, resume_file)
