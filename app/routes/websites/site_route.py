import os
import re
from fastapi import Form, Depends, responses
from app.core.security import verify_session
from app.services import website
from . import router


@router.post("/save")
async def save_site(
    domain: str = Form(...),
    mode: str = Form("simple"),
    site_type: str = Form("proxy"),
    port: int = Form(8000),
    root_dir: str = Form("/var/www/html"),
    raw_config: str = Form(""),
    _: str = Depends(verify_session),
):
    if mode != "simple" and raw_config:
        match_root = re.search(r"root\s+([^;]+);", raw_config)
        if match_root:
            root_dir = match_root.group(1).strip()

    if root_dir.startswith("/var/www/html/"):
        os.makedirs(root_dir, exist_ok=True)
        index_file = os.path.join(
            root_dir, "index.php" if site_type == "php" else "index.html"
        )

        if not os.path.exists(index_file):
            with open(index_file, "w") as f:
                if site_type == "php":
                    f.write(
                        f"<?php\necho '<h1>Welcome to {domain}</h1>';\necho '<p>PHP is working! Created via HyperionOS.</p>';\n?>"
                    )
                else:
                    f.write(
                        f"<h1>Welcome to {domain}</h1>\n<p>Static/Proxy page created via HyperionOS.</p>"
                    )

    website.save_website(
        domain=domain,
        mode=mode,
        site_type=site_type,
        port=port,
        root_dir=root_dir,
        raw_config=raw_config,
    )
    return responses.RedirectResponse(url="/websites", status_code=303)


@router.post("/toggle/{domain}")
async def toggle_site(domain: str, _: str = Depends(verify_session)):
    website.toggle_website(domain)
    return responses.RedirectResponse(url="/websites", status_code=303)


@router.post("/delete/{domain}")
async def delete_site(domain: str, _: str = Depends(verify_session)):
    website.delete_website(domain)
    return responses.RedirectResponse(url="/websites", status_code=303)
