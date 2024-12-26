import os
import requests
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def fetch_assets(api_key, org_id=None, search=None, fields=None):
    """
    Fetch all assets using the runZero API with API Key authentication.
    """
    base_url = "https://console.rumble.run/inventory"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {}

    if org_id:
        params["_oid"] = org_id  # 조직 ID 필수 시 설정
    if search:
        params["search"] = search
    if fields:
        params["fields"] = fields

    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        assets = response.json()
        return assets
    except requests.exceptions.RequestException as e:
        print(f"Error fetching assets: {e}")
        return []

def main():
    """
    Main function to fetch and display assets using API Key authentication.
    """
    api_key = os.getenv("RUNZERO_API_KEY")
    if not api_key:
        raise ValueError("API Key is missing! Set RUNZERO_API_KEY in your environment variables.")

    # Organization ID를 반드시 추가하세요.
    org_id = "your_organization_id"  # Replace with your actual organization ID
    search = None
    fields = None

    assets = fetch_assets(api_key, org_id=org_id, search=search, fields=fields)

    if assets:
        print("Fetched Assets:")
        for asset in assets:
            print(f"ID: {asset.get('id')}, Name: {asset.get('agent_name')}, IP: {asset.get('addresses')}, OS: {asset.get('os')}")
    else:
        print("No assets found.")

if __name__ == "__main__":
    main()