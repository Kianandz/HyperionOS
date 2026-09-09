import os
import pty
import subprocess
import select
import asyncio
import pwd  # <-- Tambahin import ini buat ngecek user sistem
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.templating import Jinja2Templates
from app.core.security import verify_session

router = APIRouter(prefix="/terminal", tags=["Terminal"])
templates = Jinja2Templates(directory="app/templates")

@router.get("")
async def terminal_page(request: Request, user: str = Depends(verify_session)):
    return templates.TemplateResponse(
        request=request, 
        name="pages/terminal.html", 
        context={"user": user, "active_page": "terminal"}
    )

@router.websocket("/ws")
async def terminal_websocket(websocket: WebSocket):
    await websocket.accept()
    
    # Bikin PTY (Pseudo-terminal)
    master, slave = pty.openpty()
    
    env = os.environ.copy()
    env["TERM"] = "xterm-256color"
    
    # Otomatis deteksi default shell user saat ini
    try:
        default_shell = pwd.getpwuid(os.getuid()).pw_shell
    except Exception:
        # Fallback ke bash kalau gagal deteksi
        default_shell = os.environ.get("SHELL", "/bin/bash")
    
    # Panggil shell yang sesuai (zsh/bash/fish)
    process = subprocess.Popen(
        [default_shell],
        stdin=slave, stdout=slave, stderr=slave,
        env=env, preexec_fn=os.setsid
    )
    os.close(slave)

    async def read_from_pty():
        while True:
            await asyncio.sleep(0.01)
            r, _, _ = select.select([master], [], [], 0)
            if master in r:
                data = os.read(master, 1024).decode(errors="ignore")
                if not data:
                    break
                await websocket.send_text(data)

    async def write_to_pty():
        try:
            while True:
                data = await websocket.receive_text()
                os.write(master, data.encode())
        except WebSocketDisconnect:
            pass

    task1 = asyncio.create_task(read_from_pty())
    task2 = asyncio.create_task(write_to_pty())
    
    done, pending = await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
        
    try:
        process.terminate()
    except:
        pass