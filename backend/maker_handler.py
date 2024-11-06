from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form, Cookie
import uuid
from fastapi.security import api_key
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredPowerPointLoader,
)
from langchain_postgres.vectorstores import Base
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr, conset
import os
from jose import jwt
from sqlalchemy.orm.util import identity_key
from model import (
    Answer,
    DraftPdfinsert,
    KnowledgeListUpdate,
    KnowledgeRegulation,
    Metadata,
    KnowledgeHeader,
    KnowledgeList,
    InsertKnowledgeHeader,
    ManualInput,
)
from config import db_dependency
from minio import Minio
from user_handler import verify_admin
from starlette.responses import StreamingResponse
from langchain_core.documents import Document
from sqlalchemy import desc, text
import json
import redis
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate, prompt
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from openai import OpenAI
from pydantic import BaseModel
from typing import List
import re

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

client_minio = Minio(
    MINIO_URL,
    secure=False,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
)

bucket_name = "hackathon"


@router.get("/api/maker/dashboard")
async def dashboard(db: db_dependency):
    res = (
        db.query(KnowledgeHeader.title, KnowledgeHeader.countx)
        .order_by(desc(KnowledgeHeader.countx))
        .limit(5)
        .all()
    )

    resx = [{"title": item.title, "countx": item.countx} for item in res]
    return resx


@router.post(
    "/api/maker/delete_header/{ids_header}", dependencies=[Depends(verify_admin)]
)
async def delete_knowledge_header(db: db_dependency, ids_header: str):
    try:
        res = (
            db.query(KnowledgeHeader).filter(KnowledgeHeader.ids == ids_header).first()
        )

        # ambil data ids berdasarkan header
        resx = (
            db.query(KnowledgeList.ids)
            .filter(KnowledgeList.ids_header == ids_header)
            .all()
        )

        result_ids: List[str] = [row[0] for row in resx]
        print(result_ids)

        if resx is None or res is None:
            raise HTTPException(400, detail="tidak terdapat id tsb")
        else:

            # hapus vector berdasarkan ids
            vector_store.delete(ids=result_ids)

            # soft delete header
            res.deleted_at = datetime.now()  # type: ignore
            db.commit()

            del_list = text(
                "update knowledge_list set deleted_at = current_timestamp where ids_header = :id"
            )
            db.execute(del_list, {"id": ids_header})
            db.commit()

            return "berhasil delete id tsb"

    except Exception as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(err))


# dependencies=[Depends(verify_admin)]
@router.post("/api/maker/delete_list/{ids}", dependencies=[Depends(verify_admin)])
async def delete_knowledge_list(db: db_dependency, ids: str):
    try:
        res = db.query(KnowledgeList).filter(KnowledgeList.ids == ids).first()

        res_str = str(res.ids) if res else None

        if res is None:
            raise HTTPException(400, detail="tidak terdapat id tsb")
        else:

            vector_store.delete(ids=[str(res_str)])
            res.deleted_at = datetime.now()  # type: ignore
            db.commit()

            return "berhasil delete id tsb"

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/api/maker/test_make_quest")
async def make_questx(item: Answer):
    try:
        results = vector_store.similarity_search(item.question, k=5)
        res = []

        for r in results:
            res.append(r.page_content)

        prompt = " ".join(res)

        class FormatJawaban(BaseModel):
            uraian_jawaban: str
            skor: int

        class SoalModel(BaseModel):
            soal: str
            jawaban: List[FormatJawaban]

        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Berikan 1 Soal dan 4 Opsi Jawaban pilihan ganda yang mirip antara jawaban dengan 1 jawaban benar saja (jawaban benar memiliki skor 1 sedangkan jawaban salah memiliki skor 0) untuk konteks yang diberikan oleh user",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format=SoalModel,
        )

        return response.choices[0].message.parsed

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.put("/api/maker/update_knowledge_list/{ids_header}/{ids}")
async def update_faq(db: db_dependency, item: KnowledgeListUpdate,ids_header: str, ids: str):
    if ids:
        try:
            exist = db.query(KnowledgeList).filter(KnowledgeList.ids == ids, KnowledgeList.ids_header == ids_header).first()

            if exist is None:
                raise HTTPException(
                    status_code=400, detail="Id knowledge tidak sesuai"
                )
            else:
                for val, value in vars(item).items():
                    setattr(exist, val, value)

                db.commit()
                return "Berhasil update faq"
        except Exception as err:
            raise HTTPException(status_code=500, detail=str(err))
    else:
        raise HTTPException(status_code=500, detail="idnya tidak ada")


@router.get("/api/maker/redis/{idx}")
async def test_redis(idx: str):
    try:
        r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        res = r.get(idx)
        python_list = json.loads(res)  # type: ignore

        return python_list
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/api/maker/delete_knowledge/{ids}/{ids_header}", dependencies=[Depends(verify_admin)])
async def delete_knowledge(ids: str, ids_header: str, db: db_dependency):
    if ids and ids_header:
        try:

            exists = (
                db.query(KnowledgeList)
                .filter(
                    KnowledgeList.ids == ids, KnowledgeList.ids_header == ids_header
                )
                .first()
            )
            if exists is None:
                raise HTTPException(status_code=400, detail="Id faq ga ada")
            else:
                exists.deleted_at = datetime.now()  # type: ignore
                vector_store.delete(ids=[ids])
                
                db.commit()
                return "Berhasil hapus knowledge"
        except Exception as err:
            raise HTTPException(status_code=500, detail=str(err))
    else:
        raise HTTPException(status_code=500, detail="id tidak ada")


@router.post("/api/maker/store_manual/{ids_header}")
async def store_manual(item: ManualInput, db: db_dependency, ids_header: str):
    try:

        idx = str(uuid.uuid4())
        single_docs = Document(
            id=idx,
            page_content=item.page_content,
            metadata={
                "id": idx,
                "metadata": item.model_dump_json(),
                "ids_header": ids_header,
                "file_name": "-",
                "category_id": item.category_id,
            },
        )

        vector_store.add_documents([single_docs])
        content = KnowledgeList(
            ids=single_docs.id,
            ids_header=ids_header,
            page_content=single_docs.page_content,
            file=single_docs.metadata["file_name"],
            category_id=single_docs.metadata["category_id"],
        )
        db.add(content)
        db.commit()

        return "Berhasil Insert Dokumen"
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/api/maker/store_pdf_from_redis/{idx}/{filename}/{ids_header}")
async def store_pdf_from_redis_post(
    idx: str, item: Metadata, db: db_dependency, filename: str, ids_header: str
):
    try:

        r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        res = r.get(idx)
        python_list = json.loads(res)  # type: ignore

        docs_insert = []
        for spl in python_list:
            idy = str(uuid.uuid4())
            single_docs = Document(
                id=idy,
                page_content=spl,
                metadata={
                    "id": idy,
                    "metadata": item.model_dump_json(),
                    "ids_header": ids_header,
                    "file_name": filename,
                    "category_id": 2,
                },
            )
            docs_insert.append(single_docs)

        vector_store.add_documents(
            docs_insert, ids=[doc.metadata["id"] for doc in docs_insert]
        )

        for itemx in docs_insert:
            content = KnowledgeList(
                ids=itemx.id,
                ids_header=ids_header,
                page_content=itemx.page_content,
                file=itemx.metadata["file_name"],
                category_id=itemx.metadata["category_id"],
            )
            db.add(content)
            db.commit()

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/api/maker/store_pdf_from_redis/{idx}")
async def store_pdf_from_redis(idx: str, item: Metadata):
    try:
        r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        res = r.get(idx)
        python_list = json.loads(res)  # type: ignore

        print(item)
        return python_list
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/api/maker/test_metadata")
async def post_test_metadata(file: UploadFile, db: db_dependency):
    try:

        filenamex = str(uuid.uuid4()) + ".pdf"

        file_path = f"/tmp/{filenamex}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        loader = PyPDFLoader(file_path)

        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500, chunk_overlap=200
        )

        splits = text_splitter.split_documents(docs)

        docs_insert = []

        for spl in splits:
            single_docs = spl.page_content
            docs_insert.append(single_docs)

        if os.path.exists(f"/tmp/{filenamex}"):
            os.remove(f"/tmp/{filenamex}")

        idx = str(uuid.uuid4())

        r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        r.set(idx, json.dumps(docs_insert))

        return {"idx": idx, "page": splits}

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/api/maker/get_all_header", dependencies=[Depends(verify_admin)])
async def get_all_header(db: db_dependency, search: str | None = None):
    if search:
        searchx = search.lower()
        res = (
            db.query(
                KnowledgeHeader.ids, KnowledgeHeader.title, KnowledgeHeader.image_url
            )
            .filter(
                KnowledgeHeader.deleted_at == None,
                KnowledgeHeader.title.ilike(f"%{searchx}%"),
            )
            .order_by(desc(KnowledgeHeader.countx))
            .all()
        )
        result = [
            {"ids": item.ids, "title": item.title, "image_url": item.image_url}
            for item in res
        ]
        return {"data": result}
    else:
        res = (
            db.query(
                KnowledgeHeader.ids, KnowledgeHeader.title, KnowledgeHeader.image_url
            )
            .filter(KnowledgeHeader.deleted_at == None)
            .order_by(desc(KnowledgeHeader.countx))
            .all()
        )

        result = [
            {"ids": item.ids, "title": item.title, "image_url": item.image_url}
            for item in res
        ]
        return {"data": result}


@router.get("/api/maker/get_file/{ids}")
async def get_file_minio(ids: str):

    extx = ids.split(".")
    match extx[1]:
        case "pdf":
            headers = {"Content-Disposition": f'inline; filename="{ids}"'}
            res = client_minio.get_object(bucket_name, ids)
            return StreamingResponse(res, media_type="application/pdf", headers=headers)
        case "pptx":
            res = client_minio.get_object(bucket_name, ids)
            return StreamingResponse(
                res,
                media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )
        case "docx":
            res = client_minio.get_object(bucket_name, ids)
            return StreamingResponse(
                res,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        case _:
            raise HTTPException(status_code=400, detail="ext tidak sesuai")


@router.get("/api/maker/image/{image_id}")
async def get_image_minio(image_id: str):
    imagex = image_id.split(".")
    res_image = client_minio.get_object(bucket_name, image_id)
    return StreamingResponse(res_image, media_type="image/" + imagex[1])


@router.post("/api/maker/create_header", dependencies=[Depends(verify_admin)])
async def create_header(
    category_id: Annotated[int, Form()],
    title: Annotated[str, Form()],
    db: db_dependency,
    image: UploadFile | None = None,
    user_69: Annotated[str | None, Cookie()] = None,
):
    if user_69:
        idx = str(uuid.uuid4())
        res = jwt.decode(user_69, JWT_SECRET, algorithms=["HS256"])
        ids_user = res["ids"]

        if image:
            try:
                _, imageext = os.path.splitext(str(image.filename))
                imagenamex = str(uuid.uuid4()) + imageext

                file_path = f"/tmp/{imagenamex}"
                with open(file_path, "wb") as f:
                    f.write(image.file.read())

                insert = InsertKnowledgeHeader(
                    ids=idx,
                    image_url=imagenamex,
                    category_id=category_id,
                    title=title,
                    creator_ids=ids_user,
                )

                client_minio.fput_object(
                    bucket_name,
                    imagenamex,
                    file_path,
                )

                if os.path.exists(f"/tmp/{imagenamex}"):
                    os.remove(f"/tmp/{imagenamex}")
                else:
                    print("ga bisa hapus file")

                header = KnowledgeHeader(**insert.model_dump())
                db.add(header)
                db.commit()
                return {"ids_header": idx}
            except Exception as err:
                raise HTTPException(status_code=500, detail=str(err))
        else:

            # gambar default
            imagenamex = "8cc26a96-7580-4cfd-b327-80acdaf1f278.webp"
            insert = InsertKnowledgeHeader(
                ids=idx,
                image_url=imagenamex,
                category_id=category_id,
                title=title,
                creator_ids=ids_user,
            )

            header = KnowledgeHeader(**insert.model_dump())
            db.add(header)
            db.commit()

            return {"ids_header": idx}
    else:
        raise HTTPException(status_code=400, detail="Token tidak valid")


@router.post("/api/maker/upload_file")
async def upload_pdf(file: UploadFile):

    try:

        _, filext = os.path.splitext(str(file.filename))
        filenamex = str(uuid.uuid4()) + filext

        file_path = f"/tmp/{filenamex}"

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        bucket_name = "hackathon"

        found = client_minio.bucket_exists(bucket_name)
        if not found:
            client_minio.make_bucket(bucket_name)
            print("Created bucket", bucket_name)
        else:
            print("Bucket", bucket_name, "already exists")

        client_minio.fput_object(
            bucket_name,
            filenamex,
            file_path,
        )

        if os.path.exists(f"/tmp/{filenamex}"):
            os.remove(f"/tmp/{filenamex}")
        else:
            print("ga bisa hapus file")

        return filenamex  # type: ignore

    except Exception as e:
        return {"message": str(e)}


@router.get("/api/maker/get_data_from_header/{ids}")
async def get_data_from_header(ids: str, db: db_dependency):
    res = (
        db.query(KnowledgeList.ids, KnowledgeList.page_content, KnowledgeList.file)
        .filter(KnowledgeList.ids_header == ids, KnowledgeList.deleted_at == None)
        .all()
    )
    result = [
        {"ids": item.ids, "page_content": item.page_content, "file": item.file}
        for item in res
    ]
    return result


@router.post("/api/maker/store_list_from_draft/{ids_header}")
async def store_from_draft_pdf(
    draft: list[DraftPdfinsert], db: db_dependency, ids_header: str
):
    try:
        docs_insert = []
        for spl in draft:
            idx = str(uuid.uuid4())
            single_docs = Document(
                id=idx,
                page_content=spl.page_content,
                metadata={
                    "id": idx,
                    "topics": spl.metadata,
                    "ids_header": ids_header,
                    "file_name": spl.file,
                    "category_id": spl.category_id,
                },
            )
            docs_insert.append(single_docs)

        vector_store.add_documents(
            docs_insert, ids=[doc.metadata["id"] for doc in docs_insert]
        )

        for item in docs_insert:

            content = KnowledgeList(
                ids=item.id,
                ids_header=ids_header,
                page_content=item.page_content,
                file=item.metadata["file_name"],
                category_id=item.metadata["category_id"],
            )
            db.add(content)
            db.commit()

        return "berhasil insert"
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/api/maker/store_pptx")
async def store_pptx(file: UploadFile):
    try:
        filenamex = str(uuid.uuid4()) + ".pptx"
        file_path = f"/tmp/{filenamex}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        loader = UnstructuredPowerPointLoader(file_path)

        docs = loader.load()

        print(len(docs))

        if len(docs) <= 5:
            if os.path.exists(f"/tmp/{filenamex}"):
                os.remove(f"/tmp/{filenamex}")

            # return splits list

            return {"jmlh": len(docs), "page": docs}

        else:  # jika lebih dari 5 halamaan simpan text ke redis sblm ditambah metadata

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500, chunk_overlap=200
            )

            splits = text_splitter.split_documents(docs)

            docs_insert = []

            for spl in splits:
                single_docs = spl.page_content
                docs_insert.append(single_docs)

            if os.path.exists(f"/tmp/{filenamex}"):
                os.remove(f"/tmp/{filenamex}")

            idx = str(uuid.uuid4())

            r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
            r.set(idx, json.dumps(docs_insert))

            return {"jmlh": len(docs_insert), "idx": idx}

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


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


@router.post("/api/maker/store_pdf/{id_cat}/{ids_header}")
async def store_pdf(
    db: db_dependency,
    file: UploadFile,
    id_cat: int,
    ids_header: str,
    nomor: Optional[str] = Form(None),
    judul: Optional[str] = Form(None),
):
    try:

        filenamex = str(uuid.uuid4()) + ".pdf"

        file_path = f"/tmp/{filenamex}"

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        loader = PyPDFLoader(file_path)

        # upload ke bucket
        bucket_name = "hackathon"
        found = client_minio.bucket_exists(bucket_name)
        if not found:
            client_minio.make_bucket(bucket_name)
            print("Created bucket", bucket_name)
        else:
            print("Bucket", bucket_name, "already exists")

        client_minio.fput_object(
            bucket_name,
            filenamex,
            file_path,
        )

        # if os.path.exists(f"/tmp/{filenamex}"):
        #    os.remove(f"/tmp/{filenamex}")
        # else:
        #    print("tdk bs hapus file")

        docs = loader.load()

        match id_cat:
            case 1:
                if len(docs) <= 5:
                    return {"jmlh": len(docs), "page": docs, "file": filenamex}

                else:
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=1500, chunk_overlap=200
                    )

                    splits = text_splitter.split_documents(docs)

                    docs_insert = []

                    for spl in splits:
                        single_docs = spl.page_content
                        docs_insert.append(single_docs)

                    idx = str(uuid.uuid4())

                    r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
                    r.set(idx, json.dumps(docs_insert))

                    return {"jmlh": len(docs_insert), "idx": idx, "file": filenamex}
            case 2:
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
                        }

                        parsed_structure.append(current_bab)
                        current_bagian = None

                    elif line.startswith("Bagian"):
                        pending_bagian = line

                    elif pending_bagian:
                        current_bagian = {"bagian": line, "pasal": []}  # type:ignore
                        current_bab["bagian"].append(current_bagian)  # type:ignore
                        pending_bagian = None

                    elif line.startswith("Bagian"):
                        current_bagian = {"bagian": line, "pasal": []}  # type:ignore
                        current_bab["bagian"].append(current_bagian)  # type:ignore

                    # jika line dimulai dengan Pasal atau Pasa1 dan tidak ada ayatnya dan panjangya kurang dari 12 char
                    elif (
                        (line.startswith(("Pasal", "Pasa1")))
                        and "ayat" not in line
                        and len(line) <= 12
                    ):
                        current_pasal = {
                            "pasal": line,
                            "isi": "",
                        }  # Struktur Pasal baru
                        if current_bagian is None:
                            current_bab["pasal"].append(current_pasal)  # type:ignore
                        else:
                            current_bagian["pasal"].append(current_pasal)
                    elif current_pasal:
                        current_pasal["isi"] += line + " "

                ids_regulation = str(uuid.uuid4())
                flat_structure = transform_to_flat_format(parsed_structure)

                regulation = KnowledgeRegulation(
                    ids=ids_regulation,
                    ids_header=ids_header,
                    nomor=nomor,
                    judul=judul,
                    isi=flat_structure,
                )
                db.add(regulation)
                db.commit()

                converted_docu = [
                    Document(
                        id=str(uuid.uuid4()),
                        page_content=entry["content"],
                        metadata={
                            "bab": entry["bab"],
                            "bagian": entry["bagian"],
                            "pasal": entry["pasal"],
                            "ids_regulation": ids_regulation,
                        },
                    )
                    for entry in flat_structure
                ]

                # jika ada lampiran
                if index_terakhir != 0:
                    idx_terakhir = index_terakhir + 1

                    for do in docs[idx_terakhir:]:
                        single_doc = Document(
                            id=str(uuid.uuid4()),
                            page_content=re.sub(pattern, "", do.page_content),
                            metadata={
                                "bab": "Lampiran",
                                "bagian": "Lampiran",
                                "pasal": "Lampiran",
                                "ids_regulation": ids_regulation,
                            },
                        )
                        converted_docu.append(single_doc)

                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1500, chunk_overlap=200
                )

                splits = text_splitter.split_documents(converted_docu)

                split_json = []

                for spl in splits:
                    single_split = {
                        "id": str(uuid.uuid4()),
                        "page_content": spl.page_content,
                        "metadata": spl.metadata,
                        "ids_regulation": ids_regulation,
                    }
                    split_json.append(single_split)
                idx = str(uuid.uuid4())

                r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
                r.set(idx, json.dumps(split_json))

                return {"idx": idx, "file": filenamex}

            case _:
                raise HTTPException(status_code=500, detail="pilih kategori yg sesuai")
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/api/maker/store_pdf_id_cat_2/{idx}/{filename}/{ids_header}")
async def store_pdf_id_cat_2(
    idx: str, item: Metadata, db: db_dependency, filename: str, ids_header: str
):
    try:

        r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        res = r.get(idx)

        python_list = json.loads(res)  # type: ignore

        docs_insert = []
        for spl in python_list:
            idy = spl["id"]
            ids_regulation = spl["ids_regulation"]

            item.metadata.update(spl["metadata"])
            item.metadata.update(
                {
                    "id": spl["id"],
                    "file_name": filename,
                    "category_id": "2",
                    "ids_regulation": ids_regulation,
                }
            )

            single_docs = Document(
                id=idy,
                page_content=spl["page_content"],
                metadata={
                    "id": spl["id"],
                    "metadata": item.metadata,
                    "ids_header": ids_header,
                    "file_name": filename,
                },
            )
            # print(single_docs)
            docs_insert.append(single_docs)

        vector_store.add_documents(
            docs_insert, ids=[doc.metadata["id"] for doc in docs_insert]
        )

        for itemx in docs_insert:
            content = KnowledgeList(
                ids=itemx.id,
                ids_header=ids_header,
                page_content=itemx.page_content,
                file=itemx.metadata["file_name"],
                category_id=2,
            )

            db.add(content)
            db.commit()

        return "berhasil input"
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))
