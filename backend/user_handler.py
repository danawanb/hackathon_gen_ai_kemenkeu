from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, Request, Form, Cookie
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from dotenv import load_dotenv
import os
import uuid
import httpx
import time

from model import Faq, User, DoUserInsert, UserInsert, DoInsertUserRoles, UserRoles
from config import db_dependency

router = APIRouter()

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_SECRET_ID")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")
URLX = os.environ.get("REDIRECT_URI")
JWT_SECRET = os.environ.get("JWT_SECRET", "")


def is_admin(role: int, list_role: list[str]) -> bool:
    exist = False
    for i in list_role:
        if i["role_id"] == role:  # type: ignore
            exist = True
            return exist

    return exist


async def verify_admin(user_69: Annotated[str, Cookie()]):
    if user_69:
        res = jwt.decode(user_69, JWT_SECRET, algorithms=["HS256"])
        admin = res["roles"]
        status = is_admin(1, admin)
        print(f"is admin {status}")
        if status:
            return res
        else:
            raise HTTPException(status_code=403, detail="Bukan admin")
    else:
        raise HTTPException(status_code=400, detail="Token tidak valid")


@router.post("/api/user/insert_user", dependencies=[Depends(verify_admin)])
async def insert_user_dummy(db: db_dependency, item: UserInsert):
    try:
        res = (
            db.query(User.id)
            .filter(User.email == item.email, User.deleted_at == None)
            .first()
        )
        if res:
            raise HTTPException(status_code=400, detail="email sudah terdaftar")

        insert = DoUserInsert(ids=str(uuid.uuid4()), email=item.email)
        user = User(**insert.model_dump())

        db.add(user)
        db.commit()

        return "berhasil insert user"

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


# @router.get("/api/user/test_db")
async def get_user_db(db: db_dependency):
    res = db.query(Faq.id, Faq.short, Faq.long).all()
    result = [{"id": item.id, "short": item.short, "long": item.long} for item in res]
    return {"data": result}


@router.get("/api/user/auth/google", tags=["users"], response_class=RedirectResponse)
async def login_googlex():
    urlx = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"
    return RedirectResponse(urlx)


@router.post("/api/user/test_auth", tags=["user"])
async def test_auth(db: db_dependency, email: Annotated[str, Form()]):
    try:

        if email:
            existx = (
                db.query(User.ids)
                .filter(User.email == email, User.deleted_at == None)
                .first()
            )

            print(existx)
            if existx:
                res_role = [
                    row._asdict()
                    for row in db.query(UserRoles.role_id)
                    .filter(UserRoles.ids_user == existx.ids)  # type:ignore
                    .all()
                ]
                print(res_role)
                res_exist_ids = str(existx[0])
                res = {
                    "email": res_exist_ids,
                    "role": res_role,
                }
            else:
                return "email tidak ada"
            return res
        else:
            return "ga ada emailnya bro"
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/api/user/get_token_google")
async def get_token_google(user_69: Annotated[str | None, Cookie()] = None):
    if user_69:
        res = jwt.decode(user_69, JWT_SECRET, algorithms=["HS256"])
        print(res["ids"])
        print(res["roles"])
        list_res = res["roles"]

        for i in list_res:
            print(i["role_id"])

        return res["ids"]
    else:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get(
    "/api/user/auth/google/callback", tags=["user"], response_class=RedirectResponse
)
async def auth_google(code: str, db: db_dependency, res: Response):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    print("mulai ambil response")

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=data)
        access_token = token_response.json().get("access_token")

        user_info = await client.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        info = user_info.json()

    print("selesai ambil profile user")

    print("mulai query exist")
    exist = (
        db.query(User.email, User.ids)
        .filter(User.email == info["email"], User.deleted_at == None)
        .first()
    )
    if exist:
        # do kalau user udah ada

        print("mulai query role")
        res_role = [
            row._asdict()
            for row in db.query(UserRoles.role_id)
            .filter(
                UserRoles.ids_user == exist.ids, UserRoles.deleted_at == None
            )  # type:ignore
            .all()
        ]

        timex = time.time_ns()
        print(timex)

        credentials = {
            "ids": exist.ids,
            "roles": res_role,
        }
        token = jwt.encode(credentials, JWT_SECRET, algorithm="HS256")

        res.set_cookie(
            key="user_69",
            value=token,
            samesite="none",
            domain="https://tinycode.cloud",
            secure=False,
        )

        # return "user sudah ada tetapi berhasil login"
        return RedirectResponse(str(URLX))
    else:
        # do insert user karena blm exist
        ids = str(uuid.uuid4())
        insert = DoUserInsert(ids=ids, email=info["email"])
        user = User(**insert.model_dump())

        db.add(user)
        db.commit()

        idx = str(uuid.uuid4())
        role_user = DoInsertUserRoles(
            ids=idx, ids_user=ids, role_id=2, role_name="basic"
        )
        ruser = UserRoles(**role_user.model_dump())
        db.add(ruser)
        db.commit()

        res_role = [
            row._asdict()
            for row in db.query(UserRoles.role_id)
            .filter(
                UserRoles.ids_user == ids, UserRoles.deleted_at == None
            )  # type:ignore
            .all()
        ]

        credentials = {"ids": ids, "roles": res_role}
        token = jwt.encode(credentials, JWT_SECRET, algorithm="HS256")

        res.set_cookie(
            key="user_69",
            value=token,
            samesite="none",
            domain="https://tinycode.cloud",
            secure=False,
        )

        return RedirectResponse(str(URLX))


@router.get("/api/user/set_token")
async def set_token(response: Response, db: db_dependency):
    ids = "124e2bc2-f2af-4b40-bec7-509dcec11dd1"
    res_role = [
        row._asdict()
        for row in db.query(UserRoles.role_id)
        .filter(UserRoles.ids_user == ids, UserRoles.deleted_at == None)  # type:ignore
        .all()
    ]

    credentials = {"ids": ids, "roles": res_role}

    token = jwt.encode(credentials, JWT_SECRET, algorithm="HS256")
    response.set_cookie(
        key="user_69",
        value=token,
        samesite="none",
        secure=True,
    )

    return token


@router.get("/api/user/get_token")
async def get_tokenx(user_69: Annotated[str | None, Cookie()] = None):
    if user_69:
        res = jwt.decode(user_69, JWT_SECRET, algorithms=["HS256"])
        return res
    else:
        raise HTTPException(status_code=403, detail="Forbidden")
