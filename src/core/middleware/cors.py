# ---- Imports ---- #
from fastapi.middleware.cors import CORSMiddleware


# ---- Middleware Registration ---- #
def register_cors_middleware(app):

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app