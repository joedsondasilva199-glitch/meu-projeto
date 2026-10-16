import os
import sys
import uvicorn

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, "ER-OUTPUT")
    BACKEND_DIR = os.path.join(OUTPUT_DIR, "backend")

    for p in [BACKEND_DIR, OUTPUT_DIR]:
        if p not in sys.path:
            sys.path.insert(0, p)

    print("=" * 65)
    print(" INICIANDO DARKLINK / DARKLAD RECONSTRUÍDO (ER-BLACK)")
    print("=" * 65)
    print(" -> Dashboard: http://127.0.0.1:8000/")
    print(" -> Landing:   http://127.0.0.1:8000/landing.html")
    print(" -> Docs API:  http://127.0.0.1:8000/docs")
    print("=" * 65)

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
