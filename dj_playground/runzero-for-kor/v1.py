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

# 태스크 상세 정보를 사람이 읽을 수 있는 형태로 변환
def format_task_info(task):
    return f"Task Name: {task.name}, Type: {task.type}, Status: {task.status}"

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

            # 2. Tasks 데이터 (조직 내 태스크 가져오기)
            tasks = rz.Tasks(client=client).get_all(org_id=org_id)
            print(f"Retrieved {len(tasks)} tasks for Org ID {org_id}.")
            for task in tasks:
                task_info = format_task_info(task)
                print(f"Processing {task_info}")

                # 3. 태스크 결과에서 자산 데이터 추출
                if task.type in ["scan", "analysis"] and task.status == "processed":
                    print(f"Attempting to fetch results for: {task_info}")

                    # 태스크 결과 가져오기
                    task_results_url = f"https://console.runzero.com/api/v1.0/account/orgs/{org_id}/tasks/{task.id}/results"
                    response = requests.get(task_results_url, headers=headers)

                    if response.status_code == 200:
                        task_results = response.json()
                        assets = task_results.get("assets", [])
                        print(f"Retrieved {len(assets)} assets from task results for {task.name}.")
                        for asset in assets[:5]:  # 일부 자산만 출력
                            print(f"Asset ID: {asset.get('id')}, IP: {asset.get('primary_ip')}, Hostname: {asset.get('hostnames')}")
                    elif response.status_code == 404:
                        print(f"No results found for {task_info} (404). This task might not generate results.")
                    else:
                        print(f"Failed to fetch task results for {task_info}: {response.status_code}, {response.text}")

    except Exception as e:
        print(f"Error fetching data: {e}")

# 메인 실행
if __name__ == "__main__":
    fetch_data()