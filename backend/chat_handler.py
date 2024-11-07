from importlib.metadata import metadata
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form, Cookie
import uuid
from fastapi.security import api_key
from langchain_community.document_loaders import PyPDFLoader, UnstructuredPowerPointLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr
import os
from jose import jwt
from sqlalchemy.orm.util import identity_key
from model import DraftPdfinsert, Answer, InsertKnowledgeChatRecapUser, InsertKnowledgeEval, InsertKnowledgeEvalUser, InsertKnowledgeUsage, KnowledgeChatRecap, KnowledgeEval, KnowledgeUsage, Metadata, KnowledgeHeader, KnowledgeList, InsertKnowledgeRecap, InsertKnowledgeHeader
from config import db_dependency
from minio import Minio
from user_handler import verify_admin
from langchain_core.documents import Document
from sqlalchemy import text
from datetime import datetime
from re import findall
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
import redis
import json

router = APIRouter()

OPEN_API_KEY = os.environ.get("OPEN_API_KEY", "")
PG_URL = os.environ.get("PG_URL", "")
MINIO_URL = os.environ.get("MINIO_URL", "")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "")
REDIS_HOST = os.environ.get("REDIS_HOST", "")
JWT_SECRET = os.environ.get("JWT_SECRET", "")
sslrootcert = "ca_aiven.pem"

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large", api_key=SecretStr(OPEN_API_KEY)
)
connection = PG_URL + sslrootcert

llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=SecretStr(OPEN_API_KEY))

collection_name = "my_docs"

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)

client_minio = Minio(
    MINIO_URL,
    secure=False,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
)

bucket_name = "hackathon"


router = APIRouter()


@router.get("/api/char/redis_l")
async def test_redis():
    try:

        r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        r.lpush("do_create_soal", "defg")

        return "berhasil lpush"
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/api/char/redis_p")
async def test_redis_pop():
    try:
        r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        res = r.rpop("do_create_soal")
        return res

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/api/chat/insert_usage")
async def insert_usage(
    db: db_dependency,
    user_69: Annotated[str | None, Cookie()] = None,
):
    if user_69:
        try:
            users = jwt.decode(user_69, JWT_SECRET, algorithms=["HS256"])
            ids_user: str = users["ids"]

            # update if exist aja
            exist = (
                db.query(KnowledgeUsage)
                .filter(KnowledgeUsage.ids_user == ids_user)
                .first()
            )
            if exist is None:
                item = InsertKnowledgeUsage(ids_user=ids_user)
                use = KnowledgeUsage(**item.model_dump())
                db.add(use)
                db.commit()

                return "berhasil insert usage"
            else:
                exist.usage = int(exist.usage) + 1  # type: ignore
                db.commit()
                return "berhasil insert usage"

        except Exception as err:
            raise HTTPException(status_code=500, detail=str(err))
    else:
        raise HTTPException(status_code=403, detail="Tidak ada token")


@router.post("/api/chat/insert_recap")
async def insert_recap(
    db: db_dependency,
    item: InsertKnowledgeRecap,
    user_69: Annotated[str | None, Cookie()] = None,
):
    try:
        if user_69:
            users = jwt.decode(user_69, JWT_SECRET, algorithms=["HS256"])
            ids_user: str = users["ids"]

            itemx = InsertKnowledgeChatRecapUser(
                ids_list=item.ids_list,
                pertanyaan=item.pertanyaan,
                jawaban=item.jawaban,
                ids_user=ids_user,
            )

            doinsert = KnowledgeChatRecap(**itemx.model_dump())
            db.add(doinsert)
            db.commit()

            return "Berhasil insert recap"
        else:
            raise HTTPException(status_code=403, detail="Tidak ada token user")

    except Exception as err:
        print(str(err))
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/api/chat/insert_eval")
async def insert_eval(
    db: db_dependency,
    item: InsertKnowledgeEval,
    user_69: Annotated[str | None, Cookie()] = None,
):
    try:
        if user_69:
            users = jwt.decode(user_69, JWT_SECRET, algorithms=["HS256"])
            ids_user: str = users["ids"]

            itemx = InsertKnowledgeEvalUser(
                ids=str(uuid.uuid4()),
                ids_list=item.ids_list,
                pertanyaan=item.pertanyaan,
                jawaban=item.jawaban,
                feedback=item.feedback,
                ids_user=ids_user,
            )

            doinsert = KnowledgeEval(**itemx.model_dump())
            db.add(doinsert)
            db.commit()

            return "Berhasil insert evaluasi"
        else:
            raise HTTPException(status_code=403, detail="Tidak ada token user")

    except Exception as err:
        print(str(err))
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/api/chat/do_answer")
async def answer(item: Answer, db: db_dependency):
    try:
        print("mulai " + str(datetime.now()))
        quest = str(item.question)
        results = vector_store.similarity_search(quest, k=5)
        results2 = vector_store.similarity_search(quest, k=3)
        # print(results)
        # print("selesai similarity" + str(datetime.now()))
        resultsx = []

        ids_headers = []

        for rex in results:
            single_rex = rex.metadata["ids_header"]
            ids_headers.append(single_rex)

        ids = []
        for idx in results:
            single_idx = idx.id
            ids.append(single_idx)

        print("ambil file" + str(datetime.now()))

        files = (
            db.query(KnowledgeList.file)
            .filter(KnowledgeList.ids_header.in_(ids_headers))
            .group_by(KnowledgeList.file, KnowledgeList.ids_header)
            .all()
        )

        result_str = []
        for res in results:

            if isinstance(res.metadata["metadata"], str):
                res.metadata["metadata"] = json.loads(res.metadata["metadata"])

            if res.metadata.get("category_id", 0) == 2:
                single_aturan = {
                    "ids": res.id,
                    "judul": res.metadata["metadata"].get("judul", ""),
                    "nomor": res.metadata["metadata"].get("nomor", ""),
                    "aturan": res.metadata.get("metadata_aturan", ""),
                    "page_content": res.page_content,
                }
                result_str.append(single_aturan)

        headers_unique = list(set(ids_headers))

        print("mulai input countx header" + str(datetime.now()))
        # update countx pada knowledge header
        for head in headers_unique:
            sql_query = f"""
            UPDATE knowledge_header
            SET countx = (SELECT countx FROM knowledge_header WHERE ids = '{head}' LIMIT 1) + 1
            WHERE ids = '{head}';
            """
            db.execute(text(sql_query))
            db.commit()

        print("selesai input countx header" + str(datetime.now()))
        # update countx pada knowledge list
        for id in ids:
            sql_query = f"""
            UPDATE knowledge_list
            SET countx = (SELECT countx FROM knowledge_list WHERE ids = '{id}' LIMIT 1) + 1
            WHERE ids = '{id}';
            """
            db.execute(text(sql_query))
            db.commit()

        print("selesai input countx list" + str(datetime.now()))

        r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        res_redis = r.lpush("do_create_soal_list", json.dumps(ids))
        print(res_redis)

        for re in results:
            single_res = Document(page_content=re.page_content)
            resultsx.append(single_res)

        print("selesai input document" + str(datetime.now()))

        system_prompt = (
            "Kamu adalah asisten untuk tugas-tugas tanya jawab"
            "Gunakan potongan konteks berikut untuk menjawab pertanyaan"
            "Jika kamu tidak tahu jawabannya, katakan bahwa kamu tidak tahu dan permintaan maaf"
            "Jawablah dengan bahasa indonesia"
            "\n\n"
            "{context}"
        )

        print("mulai promting" + str(datetime.now()))
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", f"{quest}"),
            ]
        )

        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        res = question_answer_chain.invoke({"context": resultsx})
        print(res)
        print("jawab promting" + str(datetime.now()))
        string_list = [item[0] for item in files]

        return {
            "res": res,
            "files": string_list,
            "detail": result_str,
            "ids_list": ids,
        }

    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))
