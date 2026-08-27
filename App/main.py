from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from App.Workflow.workflow import ExecuteWorkflow

app = FastAPI(title="Job Finding App",
              version="0.1.0",
              description="API to find relavent job links based based on user career evaluation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root() -> dict:
    return{"message":"The JOB SEARCH AGENT is started...."}

@app.get("/health")
def health_check() -> dict:
    return{"status":"GOOD"}

data = set()
@app.post("/add item")
def add_new_item(item: str) -> dict:
    data.add(item)
    return{"message":f"{item} ADDED"}

@app.get("/display all items")
def display_all_item() -> dict:
    print(f"the data is:{data}")
    return{"message":f"Follow item is in the database{data}"}

@app.get("/verify-item/{item_name}")
def verify_item(item_name:str) ->dict:
    if item_name in data:
        return{"message":f"{item_name} is present in database"}
    return{"message":f"{item_name} is not present in database"}

@app.put("/update-item")
def update_item(existing_item: str, new_item: str) -> dict:
    if existing_item not in data:
        return {"message": f"{existing_item} is not present in the database"}

    data.remove(existing_item)
    data.add(new_item)
    return {"message": f"{existing_item} has been updated to {new_item}"}

@app.delete("/delete-item")
def delete_item(item: str) -> dict:
    if item not in data:
        return {"message": f"{item} is not present in the database"}

    data.remove(item)
    return {"message": f"{item} has been deleted from the database"}


@app.post("/execute-workflow")
def process_workflow():
    agent = ExecuteWorkflow()
    result = agent.run_workflow()
    return result["messages"][-1].content
    