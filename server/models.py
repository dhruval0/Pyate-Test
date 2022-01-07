from pydantic import BaseModel
from typing import List, Optional

class Priority(BaseModel):
    priority: List[str]


class Url(BaseModel):
    id: int
    url: str
    timestamp: int
    source: Optional[str]
    modules: Optional[List[str]]
    docMeta: Optional[Priority]


class Item(BaseModel):
    documents: List[Url]
    callBackUrl: Optional[str]
