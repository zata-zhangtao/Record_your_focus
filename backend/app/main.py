from __future__ import annotations

import datetime as dt
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "screenshots"
DATA_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI(title="ScreenShot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="Health check")
def root():
    return {"ok": True, "message": "ScreenShot API running"}


@app.post("/api/screenshot", summary="Upload a screenshot (PNG/JPEG)")
async def upload_screenshot(file: UploadFile = File(...)):
    # Normalize suffix
    suffix = ".png"
    if file.filename and "." in file.filename:
        suffix = "." + file.filename.rsplit(".", 1)[-1].lower()
        if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
            suffix = ".png"

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    out_path = DATA_DIR / f"shot_{ts}{suffix}"

    # Persist to disk
    content = await file.read()
    out_path.write_bytes(content)

    return JSONResponse(
        {
            "ok": True,
            "filename": out_path.name,
            "path": str(out_path),
            "size": len(content),
        }
    )


# Optional: list stored screenshots
@app.get("/api/screenshots", summary="List stored screenshots")
def list_screenshots():
    files = sorted(
        [p for p in DATA_DIR.glob("*.*") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True
    )
    return [
        {
            "filename": f.name,
            "path": str(f),
            "size": f.stat().st_size,
            "modified": dt.datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        }
        for f in files
    ]


def main():
    """Run the FastAPI application with uvicorn."""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()
