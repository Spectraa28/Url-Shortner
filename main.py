from contextlib import asynccontextmanager

from fastapi import FastAPI

from db import get_db_connection, init_db


async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    main()
