import requests
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import List, Optional
from ..config import settings


class ICDService:
    def __init__(self):
        self.token_url = "https://icdaccessmanagement.who.int/connect/token"
        self.base_url = "https://id.who.int/icd"
        self.token = None
        self.token_expiry = None
        self.client_id = settings.ICD_CLIENT_ID  # Use from config
        self.client_secret = settings.ICD_CLIENT_SECRET  # Use from config

    async def _get_token(self):
        if self.token and self.token_expiry > datetime.utcnow():
            return self.token
            
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "icdapi_access",
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.post(self.token_url, data=payload, verify=True)
            response.raise_for_status()
            data = response.json()
            self.token = data["access_token"]
            self.token_expiry = datetime.utcnow() + timedelta(seconds=data["expires_in"] - 60)
            return self.token
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ICD API token error: {str(e)}")

    async def get_mental_health_categories(self):
        try:
            token = await self._get_token()
            url = f"{self.base_url}/entity/334847586"  # Mental disorders entity
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "API-Version": "v2",
                "Accept-Language": "en"
            }
            
            response = requests.get(url, headers=headers, verify=True)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ICD categories error: {str(e)}")

    async def search_conditions(self, query: str):
        try:
            token = await self._get_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "API-Version": "v2",
                "Accept-Language": "en"
            }
            params = {
                "q": query,
                "useFlexisearch": "false",
                "flatResults": "true"
            }
            
            response = requests.get(
                f"{self.base_url}/release/11/2023-01/mms/search",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Handle both possible response formats
            if 'destinationEntities' in data:
                return data['destinationEntities']
            elif isinstance(data, list):
                return data
            else:
                raise ValueError("Unexpected API response format")
                
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=503, detail=f"ICD API connection error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")