from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import sqlite3
from pydantic import BaseModel

app = FastAPI()

userTemplates = Jinja2Templates(directory="userTemplates")
templates = Jinja2Templates(directory="templates")


def db_get_all_comments_by_project_id(project_id) -> list[tuple[str, str]]:
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute("select users.name, comments.content from users inner join comments on users.id = comments.owner_id where project_id = ?", (project_id,))
    comments = cursor.fetchall()
    conn.close()
    return comments


@app.get("/comments/{project_id}")   
async def comments(request: Request, project_id: int):
    return templates.TemplateResponse("comments.html", {"request": request, "comments": db_get_all_comments_by_project_id(project_id), "project_id": project_id})

@app.post("/comment/{project_id}")
async def comment(request: Request, project_id: int, name: str = Form(...), content: str = Form(...)):
    print(f"{project_id = } {name = } {content = }")
    
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comments (owner_id, project_id, content) VALUES ((select id from users where name = ?), ?, ?)", (name, project_id, content))
    conn.commit()
    conn.close()

    return templates.TemplateResponse("comment.html", {"request": request, "name": name, "content": content, "project_id": project_id})

@app.get("/view_project/{project_id}")
async def view_project(request: Request, project_id: int):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT link, name, description, id FROM projects WHERE id = ?", (project_id,))
    project: tuple = cursor.fetchone()
    conn.close()

    return templates.TemplateResponse("project_view.html", {"request": request, 'project': project, 'comments': db_get_all_comments_by_project_id(project_id)})


def db_get_all_projects(owner_id) -> list[tuple[str, str, str]]:
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT link, name, description, id FROM projects WHERE owner_id = ?", (owner_id,))
    projects = cursor.fetchall()
    conn.close()
    return projects

def db_get_all_projects_username(username: str) -> list[tuple[str, str, str]]:
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute("select * from projects inner join users on users.id = owner_id where users.name = ?", (username,))
    projects = cursor.fetchall()
    conn.close()
    return projects




@app.get("/userTemplates/{index}")
async def userTemplatesView(request: Request, index: int):
    return userTemplates.TemplateResponse(f"{index}.html", {"request": request})

@app.get("/{owner_id}")
async def root(request: Request, owner_id: int):
    return templates.TemplateResponse("index2.html", {"request": request, "projects": db_get_all_projects(owner_id)})


@app.get("/portfolio/{username}")
async def portfolio(request: Request, username: str):
    return templates.TemplateResponse("index.html", {"request": request, "projects": db_get_all_projects_username(username), "username": username})



@app.get("/edit/{owner_id}")
async def edit(request: Request, owner_id: int):
    print(f"works")
    return templates.TemplateResponse("edit.html", {"request": request, "projects": db_get_all_projects(owner_id), "owner_id": owner_id})

class Project(BaseModel):
    name: str
    description: str
    link: str




@app.post("/add_project/{owner_id}")
async def add_project(request: Request, owner_id: int, name: str = Form(...), description: str = Form(...), link: str = Form(...)):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO projects (owner_id, name, description, link) VALUES (?, ?, ?, ?)", (owner_id, name, description, link))
    conn.commit()
    conn.close()
    
    return templates.TemplateResponse("project_component.html", {"request": request, "name": name, "description": description , 'link': link, "owner_id": owner_id})

@app.post("/delete_project")
async def delete_project(request: Request, owner_id: int = Form(...), project_id: int =  Form(...)):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE owner_id = ? AND id = ?", (owner_id, project_id))
    conn.commit()
    conn.close()

    return templates.TemplateResponse("nothing.html", {"request": request})

@app.get("/edit_project/{project_id}")
async def edit_project(request: Request, project_id: int):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, description, link FROM projects WHERE id = ?", (project_id,))
    projects: tuple = cursor.fetchone()
    conn.close()

    name, description, link = projects

    return templates.TemplateResponse("edit_project.html", {"request": request, 'name': name, 'description': description, 'link': link, 'project_id': project_id})

@app.post("/edit_project/{project_id}")
async def db_update_project(request: Request, project_id, name: str = Form(...), description: str = Form(...), link: str = Form(...)):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE projects SET name = ?, description = ?, link = ? WHERE id = ?", (name, description, link, project_id))
    conn.commit()
    conn.close()
    return templates.TemplateResponse("project_component_edit.html", {"request": request, "name": name, "description": description , 'link': link, "project_id": project_id})