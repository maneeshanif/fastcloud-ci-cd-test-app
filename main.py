from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI! "}


@app.get("/name")
def read_root():
    return {"message": "Hello, Anees ... :)! "}



@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/test/{item_id}")
def test_endpoint(item_id: int):
    return {"item_id": item_id, "message": f"Test endpoint for item {item_id}"}