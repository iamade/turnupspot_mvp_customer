from .endpoints import sports

router.include_router(sports.router, prefix="/sports", tags=["sports"]) 