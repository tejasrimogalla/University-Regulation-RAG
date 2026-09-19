import io
import os
import sys
import zipfile
import random
from pathlib import Path
import httpx

def deploy():
    token = os.getenv("NETLIFY_AUTH_TOKEN")
    if not token:
        token = "nfp_wtYg9j2h9R5GTEWmhK5ZKWQDwt8uaniw3b6d"
    project_root = Path(__file__).resolve().parent.parent
    dist_dir = project_root / "frontend" / "dist"

    if not dist_dir.exists() or not (dist_dir / "index.html").exists():
        print("Error: frontend/dist not found. Please build frontend first.")
        sys.exit(1)

    print("Zipping frontend/dist files...")
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in dist_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(dist_dir)
                zf.write(file, arcname)

    zip_bytes = zip_buffer.getvalue()
    print(f"Zip created ({len(zip_bytes) / 1024:.1f} KB).")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    client = httpx.Client(timeout=45.0)

    # 1. Create a new Netlify site
    site_name = f"unirag-assistant-{random.randint(1000, 9999)}"
    print(f"Creating Netlify site: {site_name}...")
    
    site_resp = client.post(
        "https://api.netlify.com/api/v1/sites",
        json={"name": site_name},
        headers=headers
    )

    if site_resp.status_code in (422, 400):
        # Name collision, try another
        site_name = f"university-rag-{random.randint(10000, 99999)}"
        print(f"Name collision, trying: {site_name}...")
        site_resp = client.post(
            "https://api.netlify.com/api/v1/sites",
            json={"name": site_name},
            headers=headers
        )

    if site_resp.status_code not in (200, 201):
        print(f"Failed to create site ({site_resp.status_code}):", site_resp.text)
        sys.exit(1)

    site_data = site_resp.json()
    site_id = site_data["id"]
    site_url = site_data.get("ssl_url") or site_data.get("url") or f"https://{site_name}.netlify.app"
    print(f"Site created! ID: {site_id}")
    print(f"Target URL: {site_url}")

    # 2. Upload and deploy the zip
    print("Uploading production assets to Netlify...")
    deploy_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/zip"
    }

    deploy_resp = client.post(
        f"https://api.netlify.com/api/v1/sites/{site_id}/deploys",
        content=zip_bytes,
        headers=deploy_headers
    )

    if deploy_resp.status_code not in (200, 201):
        print(f"Failed to deploy assets ({deploy_resp.status_code}):", deploy_resp.text)
        sys.exit(1)

    deploy_data = deploy_resp.json()
    live_url = deploy_data.get("ssl_url") or deploy_data.get("deploy_ssl_url") or site_url

    print("\n==================================================")
    print("          NETLIFY DEPLOYMENT SUCCESSFUL!          ")
    print("==================================================")
    print(f"Live Public Site URL: {live_url}")
    print(f"Netlify Admin Panel:  https://app.netlify.com/sites/{site_name}/overview")
    print("==================================================")

if __name__ == "__main__":
    deploy()
