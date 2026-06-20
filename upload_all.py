import requests
import os

API_URL = "http://localhost:8000"

def get_token():
    resp = requests.post(f"{API_URL}/token", data={"username": "admin", "password": "admin-password"})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    return None

def upload_file(token, instance, csv_path, yaml_path):
    print(f"Uploading {csv_path} to '{instance}'...")
    headers = {"Authorization": f"Bearer {token}"}
    with open(csv_path, "rb") as csv_f, open(yaml_path, "rb") as yaml_f:
        files = {
            "file": (os.path.basename(csv_path), csv_f.read(), "text/csv"),
            "template": (os.path.basename(yaml_path), yaml_f.read(), "text/yaml")
        }
    resp = requests.post(
        f"{API_URL}/upload-metadata",
        params={"instance": instance},
        files=files,
        headers=headers
    )
    if resp.status_code == 200:
        print(f"✅ Ingestion successful: {resp.json()}")
        return True
    else:
        print(f"❌ Ingestion failed ({resp.status_code}): {resp.text}")
        return False

def reinitialize_db(token, instance):
    print(f"Reinitializing database: {instance}...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{API_URL}/config/databases/{instance}/reinitialize", headers=headers)
    if resp.status_code == 200:
        print(f"✅ Reinitialized {instance} successfully.")
    else:
        print(f"❌ Failed to reinitialize {instance}: {resp.status_code} - {resp.text}")

def main():
    token = get_token()
    if not token:
        print("Failed to authenticate.")
        return
        
    # Reinitialize first to ensure a clean state
    reinitialize_db(token, "clinical")
    reinitialize_db(token, "genomic")
        
    uploads = [
        ("clinical", "data/clinical_projects.csv", "data/yaml/clinical_projects.yaml"),
        ("clinical", "data/clinical_studies.csv", "data/yaml/clinical_studies.yaml"),
        ("clinical", "data/clinical_patients.csv", "data/yaml/clinical_patients.yaml"),
        
        ("genomic", "data/genomic_projects.csv", "data/yaml/genomic_projects.yaml"),
        ("genomic", "data/genomic_studies.csv", "data/yaml/genomic_studies.yaml"),
        ("genomic", "data/genomic_samples.csv", "data/yaml/genomic_samples.yaml"),
    ]
    
    for instance, csv, yml in uploads:
        upload_file(token, instance, csv, yml)

if __name__ == "__main__":
    main()
