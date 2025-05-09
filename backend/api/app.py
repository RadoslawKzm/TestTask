import typing
import uuid
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.middleware import is_valid_uuid4
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette import status
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from backend.api.routers import about_router, healthcheck_router, person_router
from backend.database.postgres.session import DbContext, init_db
from backend.loguru_logger.logger_setup import log_config, logger_setup


@asynccontextmanager
async def lifespan(func_app: FastAPI) -> typing.AsyncContextManager[None]:
    logger_setup()
    init_db()
    db_context = DbContext()
    yield
    if db_context.engine is not None:
        await db_context.close()


app = FastAPI(lifespan=lifespan, root_path="/api")

app.include_router(router=about_router)
app.include_router(router=healthcheck_router)
app.include_router(router=person_router)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["X-Requested-With", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)


@app.middleware("http")
async def log_user_metadata(
    request: Request, call_next: typing.Any
) -> typing.Any:
    client_ip: str = request.client.host
    client_port: int = request.client.port
    logger.info(f"{request.method} {request.url.path}")
    logger.debug(f"IP={client_ip}, Port={client_port}")
    return await call_next(request)


@app.middleware("http")
async def exception_logger(
    request: Request, call_next: typing.Any
) -> typing.Any:
    response = await call_next(request)
    log_msg: str = (
        f"{request.method} {request.url.path} {response.status_code}"
    )
    metadata_str = log_msg
    logger.opt(lazy=True).info(log_msg)
    if response.status_code < 400:
        logger.opt(lazy=True).debug(metadata_str)
    elif response.status_code == 422:
        logger.opt(lazy=True).log(
            log_config.request_validation_exception, metadata_str
        )
    elif 400 <= response.status_code < 500:
        logger.opt(lazy=True).log(log_config.http_exception, metadata_str)
    elif response.status_code == 501:
        logger.opt(lazy=True).exception(
            log_config.unexpected_exception, metadata_str
        )
    else:
        logger.opt(lazy=True).exception(
            log_config.handled_internal_exception, metadata_str
        )
    return response


def init_listeners(func_app: FastAPI) -> FastAPI:
    logger.info("Initializing global exception handlers.")

    @func_app.exception_handler(HTTPException)
    async def custom_http_exception_handler(
        request: Request, exc: HTTPException
    ) -> Response:
        headers = getattr(exc, "headers", None)
        logger.opt(lazy=True).log(
            log_config.http_exception,
            "Traceback: {traceback}, Request: {request}, Headers: {headers}",
            traceback=lambda: f"{exc}",
            request=lambda: f"{request}",
            headers=lambda: f"{headers}",
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": f"{exc.detail}"},
            headers=headers,
        )

    @func_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> Response:
        headers = getattr(exc, "headers", None)
        msg = {
            "detail": "Request validation failed",
            "message": exc.args[0][0]["msg"],
        }
        logger.opt(lazy=True).log(
            log_config.request_validation_exception,
            "Traceback: {traceback}, Request: {request}, Headers: {headers}",
            traceback=lambda: f"{exc}",
            request=lambda: f"{request}",
            headers=lambda: f"{headers}",
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=msg,
            headers=headers,
        )

    @func_app.exception_handler(Exception)
    async def custom_generic_exception_handler(
        request: Request, exc: Exception
    ) -> Response:
        headers = getattr(exc, "headers", None)
        logger.opt(lazy=True).log(
            log_config.request_validation_exception,
            "Traceback: {traceback}, Request: {request}, Headers: {headers}",
            traceback=lambda: f"{exc}",
            request=lambda: f"{request}",
            headers=lambda: f"{headers}",
        )
        return JSONResponse(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            content={
                "detail": "Internal Server Error. "
                "Our team is already working on it."
            },
            headers=headers,
        )

    return func_app


app = init_listeners(app)

app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-ID",
    update_request_header=True,
    generator=lambda: uuid.uuid4().hex,
    validator=is_valid_uuid4,
    transformer=lambda a: a,
)
