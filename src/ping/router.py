from fastapi import APIRouter

router = APIRouter(
    tags=["Проверка"]
)

@router.get(
    "/ping", 
    status_code=200,
    summary="Проверка доступности сервера",
    description="""Этот эндпоинт используется для проверки готовности сервера обрабатывать запросы.
        \nЧекер программа будет ждать первый успешный ответ и затем начнет выполнение тестовых сценариев.
    """
)
async def ping():
    return "ok"