from fastapi import FastAPI

from backend.api.routes import admin, customer, onboarding

app = FastAPI(title="OnBoardIQ")

app.include_router(customer.router)
app.include_router(onboarding.router)
app.include_router(admin.router)


@app.get("/")
def home():
    return {"message": "OnBoardIQ API running"}
