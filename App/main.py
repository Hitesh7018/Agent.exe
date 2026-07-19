from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(name="Job Finding API",
              version="0.1.0",
              description="API to find relevant and best jobs to apply based on my profile")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # "*" also covers the null origin sent by file:// pages
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "The Job finding API is live...."}

@app.get("/health")
def health_check():
    return {"status": "OK"}

data = set()
@app.post("/add_item")
def add_new_item(item: str) -> dict:
    data.add(item)
    return {"message": f"Item '{item}' added successfully."}

@app.get("/display-all-items")
def display_all_items() -> dict:
    print(f"the data is : {data}")
    return {"message": f"following items are added to the data : {data}"}

@app.get("/verify-item/{item_name}")
def verify_item(item_name: str) -> dict:
    if item_name in data:
        return {"message": f"{item_name} is present in the database"}
    return {"message": f"{item_name} is not present in the database"}

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

@app.delete("/delete-all-items")
def delete_all_items() -> dict:
    data.clear()
    return {"message": "All items have been deleted from the database"}
from App.workflows.workflow import ExecuteWorkflow

@app.post("/execute-workflow")
def process_workflow():
    agent = ExecuteWorkflow()
    result = agent.run_workflow()
    return result["messages"][-1].content