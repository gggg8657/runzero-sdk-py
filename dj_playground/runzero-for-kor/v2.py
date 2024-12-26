import runzero
import runzero.api as rz
import os
from dotenv import load_dotenv
import requests

# .env 파일에서 환경 변수 로드
load_dotenv()

# Client ID와 Client Secret 가져오기
MY_CLIENT_ID = os.getenv("MY_CLIENT_ID")
MY_CLIENT_SECRET = os.getenv("MY_CLIENT_SECRET")

if not MY_CLIENT_ID or not MY_CLIENT_SECRET:
    raise ValueError("Client ID or Client Secret is missing!")

# runZero 클라이언트 init
client = runzero.Client()

# 인증 처리
try:
    client.oauth_login(MY_CLIENT_ID, MY_CLIENT_SECRET)
    print("Successfully authenticated with runZero API.")
except Exception as e:
    print(f"Authentication failed: {e}")
    exit()

# Access Token 가져오기
def get_access_token():
    url = "https://console.runzero.com/api/v1.0/account/api/token"
    auth = (MY_CLIENT_ID, MY_CLIENT_SECRET)
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, auth=auth, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Failed to get token: {response.status_code}, {response.text}")

# 데이터 수집 함수
def fetch_data():
    try:
        # Access Token 가져오기
        access_token = get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}

        # 1. Organizations 데이터
        orgs = rz.OrgsAdmin(client=client).get_all()
        print(f"Retrieved {len(orgs)} organizations.")
        for org in orgs:
            print(f"Org ID: {org.id}, Org Name: {org.name}")

        # 모든 org_id 목록 가져오기
        org_ids = [org.id for org in orgs]

        # 각 org_id별 데이터 수집
        for org_id in org_ids:
            print(f"\nFetching data for Organization ID: {org_id}")

            # 2. Sites 데이터
            sites = rz.Sites(client=client).get_all(org_id=org_id)
            print(f"Retrieved {len(sites)} sites for Org ID {org_id}.")
            for site in sites:
                print(f"Site ID: {site.id}, Site Name: {site.name}")

                # 3. Assets 데이터
                assets_url = f"https://console.runzero.com/api/v1.0/account/orgs/{org_id}/sites/{site.id}/assets"
                assets_response = requests.get(assets_url, headers=headers)
                if assets_response.status_code == 200:
                    assets = assets_response.json()
                    print(f"Retrieved {len(assets)} assets for Site ID {site.id}.")
                    for asset in assets[:5]:  # 일부 자산만 출력
                        print(f"Asset ID: {asset.get('id')}, IP: {asset.get('primary_ip')}, Hostname: {asset.get('hostnames')}")
                else:
                    print(f"Failed to fetch assets for Site ID {site.id}: {assets_response.status_code}, {assets_response.text}")

                # 4. Services 데이터
                services_url = f"https://console.runzero.com/api/v1.0/account/orgs/{org_id}/sites/{site.id}/services"
                services_response = requests.get(services_url, headers=headers)
                if services_response.status_code == 200:
                    services = services_response.json()
                    print(f"Retrieved {len(services)} services for Site ID {site.id}.")
                    for service in services[:5]:  # 일부 서비스만 출력
                        print(f"Service ID: {service.get('id')}, Name: {service.get('name')}, Port: {service.get('port')}")
                else:
                    print(f"Failed to fetch services for Site ID {site.id}: {services_response.status_code}, {services_response.text}")

    except Exception as e:
        print(f"Error fetching data: {e}")

# 메인 실행
if __name__ == "__main__":
    fetch_data()