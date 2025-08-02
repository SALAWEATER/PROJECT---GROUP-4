import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configuration
CLIENT_ID = os.getenv("ICD_CLIENT_ID")
CLIENT_SECRET = os.getenv("ICD_CLIENT_SECRET")
TOKEN_URL = "https://icdaccessmanagement.who.int/connect/token"
SEARCH_URL = "https://id.who.int/icd/release/11/2023-01/mms/search"

def test_icd_connection():
    print("\nTesting ICD API connection...")
    print(f"Client ID: {CLIENT_ID}")
    print(f"Client Secret: {CLIENT_SECRET[:2]}...{CLIENT_SECRET[-2:]}")  # Show partial secret
    
    # Step 1: Get access token
    try:
        token_response = requests.post(
            TOKEN_URL,
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": "icdapi_access",
                "grant_type": "client_credentials"
            },
            timeout=10
        )
        token_response.raise_for_status()
        token_data = token_response.json()
        print("\n✅ Successfully obtained access token!")
    except Exception as e:
        print(f"\n❌ Failed to get access token: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return

    # Step 2: Test search endpoint
    try:
        headers = {
            "Authorization": f"Bearer {token_data['access_token']}",
            "Accept": "application/json",
            "API-Version": "v2",
            "Accept-Language": "en"
        }
        
        search_response = requests.get(
            SEARCH_URL,
            headers=headers,
            params={"q": "depression", "useFlexisearch": "false"},
            timeout=10
        )
        search_response.raise_for_status()
        search_data = search_response.json()
        
        print("\n✅ Successfully performed search!")
        print(f"Found {len(search_data.get('destinationEntities', []))} results")
        if len(search_data.get('destinationEntities', [])) > 0:
            first_result = search_data['destinationEntities'][0]
            print(f"\nFirst result:")
            print(f"Title: {first_result.get('title', 'N/A')}")
            print(f"Code: {first_result.get('theCode', 'N/A')}")
            print(f"ID: {first_result.get('id', 'N/A')}")
            
    except Exception as e:
        print(f"\n❌ Search failed: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Error: Missing credentials in .env file")
        print("Please ensure your .env file contains:")
        print("ICD_CLIENT_ID=your_client_id")
        print("ICD_CLIENT_SECRET=your_client_secret")
    else:
        test_icd_connection()