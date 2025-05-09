from .about.endpoints import router as about_router
from .healthcheck.endpoints import router as healthcheck_router
from .person.endpoints import router as person_router

__all__ = [about_router, healthcheck_router, person_router]
