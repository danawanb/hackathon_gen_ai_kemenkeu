from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Item(BaseModel):
    name: str
    desc: str | None = Field(default=None, max_length=10)
    price: int = Field(gt=0, le=10000)
    tax: float | None = None


class Answer(BaseModel):
    question: str = Field(min_length=10, max_length=500)


class Faq(Base):
    __tablename__ = "faq"
    id = Column(Integer, primary_key=True, autoincrement=True)
    short = Column(String)
    long = Column(String)
    deleted_at = Column(DateTime, nullable=True)


class FaqInsert(BaseModel):
    short: str = Field(default="-", max_length=50)
    long: str


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ids = Column(String)
    email = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)


class UserInsert(BaseModel):
    email: str


class DoUserInsert(BaseModel):
    ids: str
    email: str


class UserRoles(Base):
    __tablename__ = "user_roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ids = Column(String)
    ids_user = Column(String, ForeignKey("users.ids"))
    role_id = Column(Integer)
    role_name = Column(String)
    deleted_at = Column(DateTime, nullable=True)


class DoInsertUserRoles(BaseModel):
    ids: str
    ids_user: str
    role_id: int
    role_name: str


class DraftPdfinsert(BaseModel):
    page_content: str
    metadata: Dict[str, str]
    file: str
    category_id: int


class InsertKnowledgeHeader(BaseModel):
    ids: str
    image_url: str
    category_id: int
    title: str
    creator_ids: str


class KnowledgeHeader(Base):
    __tablename__ = "knowledge_header"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ids = Column(String)
    title = Column(String)
    category_id = Column(Integer)
    creator_ids = Column(String)
    countx = Column(Integer, default=0)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)


class KnowledgeList(Base):
    __tablename__ = "knowledge_list"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ids = Column(String)
    ids_header = Column(String)
    category_id = Column(Integer)
    countx = Column(Integer, default=0)
    page_content = Column(String)
    file = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)


class KnowledgeListUpdate(BaseModel):
    page_content: str


class Metadata(BaseModel):
    metadata: Dict[str, str]


class ManualInput(BaseModel):
    page_content: str
    metadata: Dict[str, str]
    category_id: int


class KnowledgeEval(Base):
    __tablename__ = "knowledge_eval"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ids = Column(String)
    ids_list = Column(JSONB)
    pertanyaan = Column(String)
    jawaban = Column(String)
    feedback = Column(Integer)
    ids_user = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)


class InsertKnowledgeEval(BaseModel):
    ids_list: List[str]
    pertanyaan: str
    jawaban: str
    feedback: int


class InsertKnowledgeRecap(BaseModel):
    ids_list: List[str]
    pertanyaan: str
    jawaban: str


class KnowledgeChatRecap(Base):
    __tablename__ = "knowledge_chat_recap"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ids_user = Column(String)
    ids_list = Column(JSONB)
    pertanyaan = Column(String)
    jawaban = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)


class InsertKnowledgeEvalUser(BaseModel):
    ids: str
    ids_list: List[str]
    pertanyaan: str
    jawaban: str
    feedback: int
    ids_user: str


class InsertKnowledgeChatRecapUser(BaseModel):
    ids_list: List[str]
    pertanyaan: str
    jawaban: str
    ids_user: str


class InsertKnowledgeUsage(BaseModel):
    ids_user: str


class KnowledgeUsage(Base):
    __tablename__ = "knowledge_usage"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ids_user = Column(String)
    usage = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)


class KnowledgeRegulation(Base):
    __tablename__ = "knowledge_regulation"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ids = Column(String)
    ids_header = Column(String)
    nomor = Column(String)
    judul = Column(String)
    isi = Column(JSONB)
    created_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
