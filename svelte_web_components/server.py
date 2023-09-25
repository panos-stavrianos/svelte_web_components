import os
import tarfile
import uuid

import uvicorn

from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from svelte_web_components import Workspace, tools
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
async def build_project(project_name: str, file: UploadFile):
    compressed_path = os.path.join("/tmp", f"{project_name}.zip")
    extracted_path = os.path.join("/tmp", project_name)
    with open(compressed_path, "wb") as buffer:
        buffer.write(await file.read())
    tools.extract_folder(compressed_path, extracted_path)
    workspace.set_components(project_name, extracted_path)
    workspace.build(project_name)

    return {"message": "ok"}


@app.on_event("startup")
def startup() -> None:
    workspace.setup_workspace()


# app.mount("/assets", StaticFiles(directory="app/assets"), name="assets")

if __name__ == "__main__":
    uvicorn.run("server:app", host='0.0.0.0', port=5050, reload=True)
