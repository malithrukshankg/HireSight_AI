import logging
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from app.api.routes.agent_route import internal_agent_router
from app.config import settings
from app.graph.jd_cv_matching_graph import build_graph, set_compiled_graph

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    schema = settings.LANGGRAPH_SCHEMA

    # Ensure the schema exists before the checkpointer tries to create its tables
    async with await psycopg.AsyncConnection.connect(
        settings.DATABASE_URL, autocommit=True
    ) as conn:
        await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        logger.info("agent-service: schema '%s' ready", schema)

    # Build a pool with search_path pinned to our schema so setup() and all
    # subsequent queries target agent_schema, not public
    pool = AsyncConnectionPool(
        conninfo=settings.DATABASE_URL,
        kwargs={"options": f"-c search_path={schema}"},
        open=False,
    )
    await pool.open()
    logger.info("agent-service: connection pool open")

    try:
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()
        set_compiled_graph(build_graph().compile(checkpointer=checkpointer))
        logger.info("agent-service: LangGraph checkpointer ready (schema=%s)", schema)
        yield
    finally:
        await pool.close()
        logger.info("agent-service: connection pool closed")


app = FastAPI(title="HireSight Agent Service", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "service": "agent-service", "version": "0.1.0"}


app.include_router(internal_agent_router)
