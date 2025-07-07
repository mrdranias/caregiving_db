from fastapi import FastAPI
from routers import adl
from routers import patients
from routers import patient_history
from routers import iadl
from routers import code_reference
from routers import hazards
from routers import risk
from routers import recommendations
from routers import contractors
from routers import services
#from routers import home_care_plan
#from routers import sdoh
from routers import prapare
from routers import social_hazards
from routers import social_risk
from routers import community_resources

app = FastAPI()
app.include_router(adl.router)
app.include_router(patients.router)
app.include_router(patient_history.router)
app.include_router(iadl.router)
app.include_router(code_reference.router)
app.include_router(hazards.router)
app.include_router(risk.router)
app.include_router(recommendations.router)
app.include_router(contractors.router)
app.include_router(services.router)
#app.include_router(home_care_plan.router)
#app.include_router(sdoh.router)
app.include_router(prapare.router)
app.include_router(social_hazards.router)
app.include_router(social_risk.router)
app.include_router(community_resources.router, prefix="/community_resources")

@app.get("/")
def root():
    return {"message": "Care Management FastAPI backend"}
