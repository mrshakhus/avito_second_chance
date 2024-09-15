import requests

def test_ping():
    # Задайте URL вашего сервера
    url = "http://localhost:8080/ping"
    
    # Выполните GET-запрос
    response = requests.get(url)
    
    # Проверьте статус код
    assert response.status_code == 200
    
    # Проверьте текст ответа
    # assert response.text == 'ok'

def test_api_ping():
    # Задайте URL вашего сервера
    url = "http://localhost:8080/api/ping"
    
    # Выполните GET-запрос
    response = requests.get(url)
    
    # Проверьте статус код
    assert response.status_code == 200
    
    # Проверьте текст ответа
    # assert response.text == 'ok'
