import requests
import json
import pytest
import allure

class TestCreateCourier:

    @allure.title("Проверяем, что курьер успешно создан")
    def test_courier_is_successfully_created(self, payload):
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier", data = payload)
        assert response.status_code == 201 and response.text == '{"ok":true}'

    @allure.title("Проверяем, что нельзя создать дубликат курьера")
    def test_cannot_create_duplicate_courier(self, payload):
        first_courier = payload
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier", data=first_courier)
        assert response.status_code == 201 and response.text == '{"ok":true}'
        second_courier = first_courier
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier", data=second_courier)
        assert response.status_code == 409 and response.json()["message"] == "Этот логин уже используется. Попробуйте другой."

    @allure.title("Проверяем, что при передаче только имени (без логина и пароля) нельзя создать курьера")
    def test_only_firstname_returns_error(self, payload):
        firstname = payload.get("firstName")
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier",
                                 data={"firstName": firstname})
        assert response.status_code == 400 and response.json()["message"] == "Недостаточно данных для создания учетной записи"

    @allure.title("Проверяем, что при передаче только логина и имени (без  пароля) нельзя создать курьера")
    def test_without_password_returns_error(self, payload):
        login = payload.get("login")
        firstname = payload.get("firstName")
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier",
                                 data={"login": login,
                                       "firstName":firstname})
        assert response.status_code == 400 and response.json()["message"] == "Недостаточно данных для создания учетной записи"

    @allure.title("Проверяем, что при передаче только имени и пароля(без логина) нельзя создать курьера")
    def test_without_password_returns_error(self, payload):
        password = payload.get("password")
        firstname = payload.get("firstName")
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier",
                                 data={"password": password,
                                       "firstName": firstname})
        assert response.status_code == 400 and response.json()["message"] == "Недостаточно данных для создания учетной записи"


class TestCourierLogin:
    @allure.title("Проверяем успешный логин курьера")
    def test_login_is_successful(self, payload):
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier", data=payload)
        assert response.status_code == 201 and response.text == '{"ok":true}'
        login = payload.get("login")
        password = payload.get("password")
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier/login",
                                 data={"login": login, "password": password})
        assert response.status_code == 200 and "id" in response.json()

    @allure.title("Проверяем, что при передаче только логина приходит ошибка")
    @pytest.mark.xfail(reason="Баг API: падает с 504 ошибкой")
    def test_login_without_password_returns_error(self, payload):
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier", data=payload)
        assert response.status_code == 201 and response.text == '{"ok":true}'
        login = payload.get("login")
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier/login",
                                 data={"login": login})
        assert response.status_code == 400 and response.json()["message"] == "Недостаточно данных для входа"

    @allure.title("Проверяем, что при передаче только пароля приходит ошибка")
    def test_login_without_login_returns_error(self, payload):
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier", data=payload)
        assert response.status_code == 201 and response.text == '{"ok":true}'
        password = payload.get("password")
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier/login",
                                 data={"password": password})
        assert response.status_code == 400 and response.json()["message"] == "Недостаточно данных для входа"

    @allure.title("Проверяем, что без предварительного создания пользователя приходит ошибка, т.к. такого пользователя нет")
    def test_login_nonexistent_user_returns_error(self, payload):
        login = payload.get("login")
        password = payload.get("password")
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier/login",
                                 data={"login": login, "password": password})
        assert response.status_code == 404 and response.json()["message"] == "Учетная запись не найдена"


class TestDeleteCourier:
    @allure.title("Проверяем удаление курьера")
    def test_courier_is_deleted(self, payload):
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier", data=payload)
        assert response.status_code == 201 and response.text == '{"ok":true}'
        login = payload.get("login")
        password = payload.get("password")
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier/login",
                                 data={"login": login, "password": password})
        created_courier = response.json()
        courier_id = created_courier['id']
        delete_response = requests.delete("https://qa-scooter.praktikum-services.ru/api/v1/courier/" + str(courier_id))
        assert delete_response.status_code == 200

class TestCreateOrder:
    colors = ["", '"color": ["BLACK"]', '"color": ["GREY"]', '"color": ["BLACK", "GREY"]']
    @allure.title("Проверяем успешное создание заказа со всеми обязательными полями и разными комбинациями цветов")
    @pytest.mark.parametrize("color", colors)
    def test_order_is_created(self, order_data, color):
        order_data += color
        order_data = json.dumps(order_data)
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/orders", data=order_data)
        assert response.status_code == 201 and "track" in response.json()


class TestGetOrders:
    @allure.title("Проверяем успешное получение списка заказов по id курьера")
    def test_get_order_list_returns_body(self, payload):
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier", data=payload)
        assert response.status_code == 201 and response.text == '{"ok":true}'
        login = payload.get("login")
        password = payload.get("password")
        response = requests.post("https://qa-scooter.praktikum-services.ru/api/v1/courier/login",
                                 data={"login": login, "password": password})
        created_courier = response.json()
        courier_id = created_courier['id']
        params = {"courierId" : courier_id}
        response = requests.get("https://qa-scooter.praktikum-services.ru/api/v1/orders", params=params)
        assert response.status_code == 200 and "orders" in response.text



