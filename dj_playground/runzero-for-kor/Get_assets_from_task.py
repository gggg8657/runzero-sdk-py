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

# runZero 클라이언트 초기화
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
def fetch_assets():
    try:
        # Access Token 가져오기
        access_token = get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}

        # Organizations 데이터 가져오기
        orgs = rz.OrgsAdmin(client=client).get_all()
        print(f"Retrieved {len(orgs)} organizations.")

        for org in orgs:
            org_id = org.id
            print(f"\nFetching tasks for Organization ID: {org_id}")

            # Tasks 데이터 가져오기
            tasks = rz.Tasks(client=client).get_all(org_id=org_id)
            print(f"Retrieved {len(tasks)} tasks for Organization ID: {org_id}.")

            for task in tasks:
                if task.type in ["scan", "analysis"] and task.status == "processed":
                    print(f"Processing Task: {task.name} (ID: {task.id})")

                    # 태스크 결과에서 자산 데이터 추출
                    task_results_url = f"https://console.runzero.com/api/v1.0/account/orgs/{org_id}/tasks/{task.id}/results"
                    response = requests.get(task_results_url, headers=headers)

                    if response.status_code == 200:
                        task_results = response.json()
                        assets = task_results.get("assets", [])
                        print(f"Retrieved {len(assets)} assets from task: {task.name}")

                        # 자산 정보 출력
                        for asset in assets:
                            print(f"Asset ID: {asset.get('id')}, IP: {asset.get('primary_ip')}, Hostname: {asset.get('hostnames')}")
                    elif response.status_code == 404:
                        print(f"No results found for Task: {task.name} (404).")
                    else:
                        print(f"Failed to fetch results for Task: {task.name}: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error fetching assets: {e}")

# 메인 실행
if __name__ == "__main__":
    fetch_assets()