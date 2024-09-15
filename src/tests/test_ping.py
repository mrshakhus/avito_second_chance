from httpx import AsyncClient


async def test_ping(
    ac: AsyncClient
):
    response = await ac.get("/api/ping")

    assert response.status_code == 200
    assert response.json() == "ok"

# def test_ping():
#     # Задайте URL вашего сервера
#     url = "http://localhost:8000/ping"
    
#     # Выполните GET-запрос
#     response = requests.get(url)
    
#     # Проверьте статус код
#     assert response.status_code == 200
    
#     # Проверьте текст ответа
#     # assert response.text == 'ok'

# def test_api_ping():
#     # Задайте URL вашего сервера
#     url = "http://localhost:8000/api/ping"
    
#     # Выполните GET-запрос
#     response = requests.get(url)
    
#     # Проверьте статус код
#     assert response.status_code == 200
    
#     # Проверьте текст ответа
#     # assert response.text == 'ok'
