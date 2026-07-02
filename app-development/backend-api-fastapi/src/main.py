"""FastAPI backend starter: CRUD for one resource over SQLite via SQLModel.

Run with:
    uvicorn src.main:app --reload
"""
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select

app = FastAPI(title="backend-api-demo")

engine = create_engine("sqlite:///app.db")


class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    done: bool = False


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


@app.post("/items", response_model=Item)
def create_item(item: Item, session: Session = Depends(get_session)):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@app.get("/items", response_model=list[Item])
def list_items(session: Session = Depends(get_session)):
    return session.exec(select(Item)).all()


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="item not found")
    return item


# TODO: add /signup and /login routes with password hashing + JWT issuance
# (see the security-review checklist item in this subtopic's README)
