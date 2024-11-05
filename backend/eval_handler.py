from fastapi import APIRouter, HTTPException
from config import db_dependency
from model import KnowledgeEval

router = APIRouter()


@router.get("/api/eval/get_eval")
async def get_eval(db: db_dependency):
    try:
        res = (
            db.query(
                KnowledgeEval.ids,
                KnowledgeEval.jawaban,
                KnowledgeEval.pertanyaan,
                KnowledgeEval.feedback,
                KnowledgeEval.ids_list,
                KnowledgeEval.ids_user,
            )
            .filter(KnowledgeEval.deleted_at == None)
            .all()
        )
        resx = [
            {
                "ids": item.ids,
                "pertanyaan": item.pertanyaan,
                "jawaban": item.jawaban,
                "feedback": item.feedback,
                "ids_list": item.ids_list,
                "ids_user": item.ids_user,
            }
            for item in res
        ]
        return resx
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
