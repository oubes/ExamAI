from fastapi import FastAPI
from app.core.config import settings
from app.core.state_graph.graph_manager import orchestrator
from app.api.v1.endpoints.submission import submit

app = FastAPI(
    title="ExamAI",
    description="An intelligent assessment engine that automates grading, enforces trust and quality, and continuously personalizes learning through adaptive exam generation.",
    version=settings.version,
)

app.include_router(
    router=submit,
    prefix="/submit",
    tags=["submit"]
)

print("DATABASE_URL:", settings.DATABASE_URL)
print("VERSION:", settings.version)


## Testing
result = orchestrator.invoke(
    {
        "msg": "Hello World" 
    } # type: ignore
)
print(result)

print("DATABASE_URL:", settings.DATABASE_URL)
print("VERSION:", settings.version)
