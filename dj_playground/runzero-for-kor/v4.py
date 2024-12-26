import os

from runzero_sdk.exceptions import RunZeroAPIError

def initialize_client():
    """
    Initialize the RunZeroClient with environment variables.
    """
    client_id = os.getenv('RUNZERO_CLIENT_ID')
    client_secret = os.getenv('RUNZERO_CLIENT_SECRET')

    if not client_id or not client_secret:
        raise ValueError("Please set RUNZERO_CLIENT_ID and RUNZERO_CLIENT_SECRET in your environment variables.")

    return RunZeroClient(client_id=client_id, client_secret=client_secret)

def get_all_assets(client):
    """
    Fetch all assets from the account.
    """
    try:
        assets = client.assets.list()
        for asset in assets:
            print(f"Asset ID: {asset.id}, Name: {asset.name}, IP: {asset.ip}, OS: {asset.os}")
    except RunZeroAPIError as e:
        print(f"Error fetching assets: {e}")

def get_all_agents(client):
    """
    Fetch all agents from the account.
    """
    try:
        agents = client.agents.list()
        for agent in agents:
            print(f"Agent ID: {agent.id}, Name: {agent.name}, OS: {agent.os}, Version: {agent.version}")
    except RunZeroAPIError as e:
        print(f"Error fetching agents: {e}")

def get_all_scans(client):
    """
    Fetch all scans from the account.
    """
    try:
        scans = client.scans.list()
        for scan in scans:
            print(f"Scan ID: {scan.id}, Name: {scan.name}, Status: {scan.status}")
    except RunZeroAPIError as e:
        print(f"Error fetching scans: {e}")

def get_all_vulnerabilities(client):
    """
    Fetch all vulnerabilities from the account.
    """
    try:
        vulnerabilities = client.vulnerabilities.list()
        for vuln in vulnerabilities:
            print(f"Vulnerability ID: {vuln.id}, Title: {vuln.title}, Severity: {vuln.severity}")
    except RunZeroAPIError as e:
        print(f"Error fetching vulnerabilities: {e}")

def main():
    client = initialize_client()

    print("Fetching all assets...")
    get_all_assets(client)

    print("\nFetching all agents...")
    get_all_agents(client)

    print("\nFetching all scans...")
    get_all_scans(client)

    print("\nFetching all vulnerabilities...")
    get_all_vulnerabilities(client)

if __name__ == "__main__":
    main()