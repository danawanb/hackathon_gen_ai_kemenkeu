from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from config import db_dependency
from model import InsertDoEval, KnowledgeEval, KnowledgeList, KnowledgeRegulation
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain_postgres import PGVector
from openai import OpenAI
from user_handler import verify_admin

import uuid
import os

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


client = OpenAI(api_key=OPEN_API_KEY)

collection_name = "my_docs"

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)


@router.get("/api/eval/get_eval")
async def get_eval(db: db_dependency, status: int | None = None):
    try:
        res = (
            db.query(
                KnowledgeEval.ids,
                KnowledgeEval.jawaban,
                KnowledgeEval.pertanyaan,
                KnowledgeEval.feedback,
                KnowledgeEval.ids_list,
                KnowledgeEval.status_eval,
                KnowledgeEval.ids_user,
            )
            .filter(
                KnowledgeEval.deleted_at == None,
                KnowledgeEval.status_eval == status,
            )
            .all()
        )
        resx = [
            {
                "ids": item.ids,
                "pertanyaan": item.pertanyaan,
                "jawaban": item.jawaban,
                "status_eval": item.status_eval,
                "feedback": item.feedback,
                "ids_list": item.ids_list,
                "ids_user": item.ids_user,
            }
            for item in res
        ]
        return resx
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/api/eval/insert_eval", dependencies=[Depends(verify_admin)])
async def insert_eval(db: db_dependency, item: InsertDoEval):
    try:
        teks = item.page_content.split("?")

        if len(teks) != 2:
            raise HTTPException(400, detail="page content salah")

        res_eval = (
            db.query(KnowledgeEval).filter(KnowledgeEval.ids == item.ids_eval).first()
        )
        if res_eval is None:
            raise HTTPException(400, detail="tidak ada ids eval")

        res = (
            db.query(KnowledgeList.ids_header)
            .filter(KnowledgeList.ids.in_(item.ids_list))
            .group_by(KnowledgeList.ids_header)
            .all()
        )

        if res is None:
            raise HTTPException(400, detail="tidak ada ids listnya")

        res_eval.status_eval = int(1)  # type: ignore
        res_eval.jawaban = str(teks[1])  # type:  ignore

        db.commit()

        for re in res:
            re_ids_header = re[0]

            idx = str(uuid.uuid4())

            # category_id -> evaluasi
            single_docs = Document(
                id=idx,
                page_content=item.page_content,
                metadata={
                    "id": idx,
                    "ids_header": re_ids_header,
                    "category_id": 6,
                    "ids_eval": item.ids_eval,
                },
            )
            vector_store.add_documents([single_docs])

            content = KnowledgeList(
                ids=idx,
                ids_header=re.ids_header,
                page_content=item.page_content,
                file="-",
                category_id=6,
            )

            db.add(content)
            db.commit()

        return "berhasil insert evaluasi"
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
