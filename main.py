from fastapi import FastAPI
from api.router import router as router_api
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router_api)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app)