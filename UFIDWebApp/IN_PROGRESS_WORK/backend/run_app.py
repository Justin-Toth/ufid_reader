import uvicorn
from sqlmodel import Session
from app.core.db import init_db, engine
from app.main import app

if __name__ == "__main__":
    # Create the database tables if they do not exist
    with Session(engine) as session:
      init_db(session)
  
    uvicorn.run("app.main:app", 
                host="127.0.0.1", 
                port=8000, 
                reload=True
    )