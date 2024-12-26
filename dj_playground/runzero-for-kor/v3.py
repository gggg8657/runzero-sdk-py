import os
import json

from runzero.client import Client
from runzero.api import OrgsAdmin, Sites, Tasks
from runzero.api.submodule_name import Assets, Services


from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Retrieve Client ID and Client Secret from environment variables
CLIENT_ID = os.getenv("RUNZERO_CLIENT_ID")
CLIENT_SECRET = os.getenv("RUNZERO_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("Client ID or Client Secret is missing!")

# Initialize the runZero client
client = Client()

# Authenticate with the runZero API
try:
    client.oauth_login(CLIENT_ID, CLIENT_SECRET)
    print("Successfully authenticated with runZero API.")
except Exception as e:
    print(f"Authentication failed: {e}")
    exit()

# Function to fetch and return data in JSON format
def fetch_data():
    try:
        # Initialize API interfaces
        orgs_api = OrgsAdmin(client=client)
        sites_api = Sites(client=client)
        assets_api = Assets(client=client)
        services_api = Services(client=client)
        tasks_api = Tasks(client=client)

        # Fetch organizations
        orgs = orgs_api.get_all()
        org_data = [{"id": org.id, "name": org.name} for org in orgs]

        # Initialize containers for assets, services, and tasks
        all_assets = []
        all_services = []
        all_tasks = []

        # Iterate over organizations to fetch sites, assets, services, and tasks
        for org in orgs:
            org_id = org.id

            # Fetch sites for the organization
            sites = sites_api.get_all(org_id=org_id)
            site_data = [{"id": site.id, "name": site.name} for site in sites]

            for site in sites:
                site_id = site.id

                # Fetch assets for the site
                assets = assets_api.get_all(org_id=org_id, site_id=site_id)
                asset_data = [{"id": asset.id, "primary_ip": asset.primary_ip, "hostnames": asset.hostnames} for asset in assets]
                all_assets.extend(asset_data)

                # Fetch services for the site
                services = services_api.get_all(org_id=org_id, site_id=site_id)
                service_data = [{"id": service.id, "name": service.name, "port": service.port} for service in services]
                all_services.extend(service_data)

            # Fetch tasks for the organization
            tasks = tasks_api.get_all(org_id=org_id)
            task_data = [{"id": task.id, "name": task.name, "status": task.status} for task in tasks]
            all_tasks.extend(task_data)

        # Compile all data into a dictionary
        data = {
            "organizations": org_data,
            "assets": all_assets,
            "services": all_services,
            "tasks": all_tasks
        }

        # Convert the data dictionary to a JSON-formatted string
        json_data = json.dumps(data, indent=4)
        return json_data

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Main execution
if __name__ == "__main__":
    json_output = fetch_data()
    if json_output:
        print(json_output)