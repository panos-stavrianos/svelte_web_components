import os

from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from svelte_web_components import Workspace
from svelte_web_components.models import Project

workspace = Workspace()
security = HTTPBearer(auto_error=False)


async def has_access(credentials: HTTPAuthorizationCredentials = Depends(security)):
    valid_token = os.environ.get("TOKEN", None)
    if valid_token is None:
        return True
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials")
    token = credentials.credentials
    print(valid_token, token)
    if token == valid_token:
        return True
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials")


app = FastAPI(dependencies=[Depends(has_access)])


@app.get("/")
def root(request: Request):
    return {"message": "Hello World", "root_path": request.scope.get("root_path")}


@app.post("/projects")
async def set_projects(request: Request, projects: list[Project]):
    response = {}
    for project in projects:
        workspace.add_project(project.name)
        response[project.name] = workspace.components_directory_hash(project.name)

    return response


@app.post("/build/{project_name}")
async def build_project(project_name: str, request: Request, file: UploadFile):
    return {"project_name": project_name, "file_name": file.filename, "file_size": len(await file.read())}


@app.on_event("startup")
def startup() -> None:
    workspace.setup_workspace()


# app.mount("/assets", StaticFiles(directory="app/assets"), name="assets")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host='0.0.0.0', port=5050, reload=True)
