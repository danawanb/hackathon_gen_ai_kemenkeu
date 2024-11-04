from typing import Annotated, List
from fastapi import FastAPI, status, HTTPException, Cookie, Form, UploadFile, Depends
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr
from langchain_community.document_loaders import PyPDFLoader, UnstructuredPowerPointLoader, Docx2txtLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.sql.operators import is_distinct_from
from starlette.types import HTTPExceptionHandler
from model import Faq, FaqInsert, KnowledgeList, KnowledgeHeader
from sqlalchemy import DateTime, create_engine, exists, text
from datetime import datetime
from config import PG_URL, db_dependency
from fastapi_utilities import repeat_at
import helper
import model
import os
import user_handler
import maker_handler
import chat_handler
import redis
import json
import re

OPEN_API_KEY = os.environ.get("OPEN_API_KEY", "")
PG_URL = os.environ.get("PG_URL", "")
REDIS_HOST = os.environ.get("REDIS_HOST", "")
CLIENT_URL = os.environ.get("CLIENT_URL", "")

sslrootcert = "ca_aiven.pem"

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key=SecretStr(OPEN_API_KEY),
)

llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=SecretStr(OPEN_API_KEY))

connection = PG_URL + sslrootcert

collection_name = "my_docs"


vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)

app = FastAPI(docs_url=None)

origins = [
    "http://localhost:5173",
    CLIENT_URL,
    "https://tinycode.cloud",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_handler.router)
app.include_router(maker_handler.router)
app.include_router(chat_handler.router)


# deprecated perlu diupdate
@app.on_event("startup")
@repeat_at(cron="*/1 * * * *")  # every 2nd minute
async def hey(db: db_dependency):
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
    res = r.rpop("do_create_soal_list")
    if res != None:
        resx: List[str] = json.loads(res)  # type: ignore

        page_content = (
            db.query(KnowledgeList.page_content)
            .filter(KnowledgeList.ids.in_(resx))
            .all()
        )

        print(resx)


@app.get("/")
def index():
    return "Made with ❤️ and ☕"


@app.get("/db")
def index_db(db: db_dependency):
    res = db.query(Faq).all()
    return {"data": res}


@app.get("/re")
def index_x(db: db_dependency):
    res = db.query(Faq.id, Faq.short, Faq.long).all()
    result = [{"id": item.id, "short": item.short, "long": item.long} for item in res]
    return {"data": result}


@app.delete("/delete_faq/{id}")
async def delete_faq(db: db_dependency, id: int):
    res = db.query(Faq).filter(Faq.id == id, Faq.deleted_at.is_(None)).first()
    if res is None:
        raise HTTPException(400, detail="tidak terdapat id tsb")
    else:
        res.deleted_at = datetime.now()  # type: ignore
        db.commit()
        return "berhasil delete id tsb"


@app.post("/insert_faq", status_code=status.HTTP_201_CREATED)
async def insert(db: db_dependency, item: FaqInsert):
    try:

        faq = Faq(**item.model_dump())
        db.add(faq)
        db.commit()

        return "berhasil insert faq"

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@app.put("/update_faq/{id}")
async def update_faq(db: db_dependency, item: FaqInsert, id: int):
    if id:
        try:
            exist = db.query(Faq).filter(Faq.id == id).first()

            if exist is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Id faq ga ada"
                )
            else:
                for val, value in vars(item).items():
                    setattr(exist, val, value)

                db.commit()
                return "Berhasil update faq"
        except Exception as err:
            raise HTTPException(status_code=500, detail=str(err))
    else:
        raise HTTPException(status_code=500, detail="id tidak ada")


@app.get("/test_speed")
async def test_speed():
    return "test"


def transform_to_flat_format(nested_data):
    flat_data = []

    for bab in nested_data:
        bab_title = bab["bab"]

        # Add each standalone pasal under a BAB without a Bagian
        for pasal in bab.get("pasal", []):
            pasal["pasal"] = re.sub(r"Pasal(\d+)", r"Pasal \1", pasal["pasal"])
            flat_data.append(
                {
                    "bab": bab_title,
                    "bagian": None,
                    "pasal": pasal["pasal"],
                    "content": pasal["isi"],
                }
            )

        # Add each pasal under Bagian within a BAB
        for bagian in bab.get("bagian", []):
            bagian_title = bagian["bagian"]
            for pasal in bagian.get("pasal", []):
                pasal["pasal"] = re.sub(r"Pasal(\d+)", r"Pasal \1", pasal["pasal"])
                flat_data.append(
                    {
                        "bab": bab_title,
                        "bagian": bagian_title,
                        "pasal": pasal["pasal"],
                        "content": pasal["isi"],
                    }
                )

    return flat_data


@app.post("/api/upload_pdf")
async def upload_pdf(file: UploadFile):
    try:

        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        loader = PyPDFLoader(file_path)
        docs = loader.load()
        str_docs = []

        index_terakhir = 0

        # cek ada lampiran tidak

        for index, doc in enumerate(docs):
            if (
                "Ditetapkan di Jakarta" in doc.page_content
                or "Diundangkan di Jakarta" in doc.page_content
            ):
                print(f"ditemukan pada indeks {index}")
                index_terakhir = index
                break

        for doc in docs:
            str_docs.append(doc.page_content)

        str_docs = "".join(str_docs)

        pattern = r"\b(?:https?://|www\.)\S+\.(com|id|co\.id|net|org|edu)\b"
        text = re.sub(pattern, "", str_docs)

        parsed_structure = []
        current_bab = None
        current_bagian = None
        current_pasal = None
        pending_bagian = None

        for line in text.splitlines():
            line = line.strip()

            if line.startswith("BAB"):
                current_bab = {
                    "bab": line,
                    "bagian": [],
                    "pasal": [],
                }  # Struktur BAB baru dengan daftar pasal langsung
                parsed_structure.append(current_bab)
                current_bagian = None

            elif line.startswith("Bagian"):
                pending_bagian = line

            elif pending_bagian:
                current_bagian = {"bagian": line, "pasal": []}
                current_bab["bagian"].append(current_bagian)  # type:ignore
                pending_bagian = None

            elif line.startswith("Bagian"):
                current_bagian = {"bagian": line, "pasal": []}  # Struktur Bagian baru
                current_bab["bagian"].append(current_bagian)  # type:ignore

            # jika line dimulai dengan Pasal atau Pasa1 dan tidak ada ayatnya dan panjangya kurang dari 12 char
            elif (
                (line.startswith(("Pasal", "Pasa1")))
                and "ayat" not in line
                and len(line) <= 12
            ):
                current_pasal = {"pasal": line, "isi": ""}  # Struktur Pasal baru
                if current_bagian is None:
                    current_bab["pasal"].append(current_pasal)  # type:ignore
                else:
                    current_bagian["pasal"].append(current_pasal)
            elif current_pasal:
                current_pasal["isi"] += line + " "

        flat_structure = transform_to_flat_format(parsed_structure)

        converted_docu = [
            Document(
                page_content=entry["content"],
                metadata={
                    "bab": entry["bab"],
                    "bagian": entry["bagian"],
                    "pasal": entry["pasal"],
                },
            )
            for entry in flat_structure
        ]

        # jika ada lampiran
        if index_terakhir != 0:
            idx_terakhir = index_terakhir + 1

            for do in docs[idx_terakhir:]:
                single_doc = Document(
                    page_content=re.sub(pattern, "", do.page_content),
                    metadata={
                        "bab": "Lampiran",
                        "bagian": "Lampiran",
                        "pasal": "Lampiran",
                    },
                )
                converted_docu.append(single_doc)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500, chunk_overlap=200
        )

        splits = text_splitter.split_documents(converted_docu)

        if os.path.exists(f"/tmp/{file.filename}"):
            os.remove(f"/tmp/{file.filename}")
        else:
            print("ga bisa hapus file")

        return {"message": splits}  # type: ignore
    except Exception as e:
        return {"message": str(e)}


@app.post("/upload")
async def upload_pptx(file: UploadFile):
    try:
        file_path = f"/tmp69/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        if os.path.exists(file_path):
            print(f"File {file_path} successfully saved.")
        else:
            print("Failed to save file.")
        try:
            loader = UnstructuredPowerPointLoader(file_path)
            data = loader.load()

            if os.path.exists(f"/tmp69/{file.filename}"):
                os.remove(f"/tmp69/{file.filename}")
            else:
                print("ga bisa hapus file")

            return {"message": data}
        except Exception as err:
            return {"message": str(err)}
    except Exception as e:
        return {"message": str(e)}


@app.get("/search")
async def search_ember(query: str | None = None):
    if query:
        results = vector_store.similarity_search(query, k=5)
        res = []

        for r in results:
            res.append(r.page_content)

        return res
    else:
        return "apa yang dicari"


@app.post("/test/{quotes}")
async def insert_test(quotes: str, item: model.Item):
    if item.price > 100:
        return HTTPException(
            status_code=400,
            detail=f"nilai anda adalah {item.price} melebih batas maksimal yakni 100",
        )
    match quotes:
        case "silahkan":
            return helper.resx(200, "berhasil ambil data", item)
        case "no":
            print(quotes)
            return helper.resx(200, "success", item)
        case _:
            return HTTPException(status_code=400, detail="tidak ada quotesnya")
