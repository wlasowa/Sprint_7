import requests
import random
import string
import pytest
import allure
import urls


def generate_random_string(length):
    letters = string.ascii_lowercase
    random_string = "".join(random.choice(letters) for i in range(length))
    return random_string


@allure.step("Создать курьера для теста")
def register_new_courier_and_return_login_password():
    login_pass = []

    login = generate_random_string(10)
    password = generate_random_string(10)
    first_name = generate_random_string(10)

    payload = {"login": login, "password": password, "firstName": first_name}

    response = requests.post(f"{urls.BASE_URL}/api/v1/courier", json=payload)

    if response.status_code == 201:
        login_pass.append(login)
        login_pass.append(password)
        login_pass.append(first_name)

    return login_pass


class BaseCourierApi:
    def setup_method(self):
        self.login = None
        self.password = None

    def teardown_method(self):
        if self.login is not None and self.password is not None:
            self.delete_courier()

    @allure.step("Удалить курьера после теста")
    def delete_courier(self):
        login_response = requests.post(
            f"{urls.BASE_URL}/api/v1/courier/login",
            json={"login": self.login, "password": self.password},
        )

        courier_id = login_response.json()["id"]

        delete_response = requests.delete(
            f"{urls.BASE_URL}/api/v1/courier/{courier_id}"
        )
        assert delete_response.status_code == 200


class TestCreateCourierApi(BaseCourierApi):
    @allure.title("Создание курьера")
    @allure.description("Курьер создаётся с уникальным логином и паролем")
    def test_create_courier(self):
        self.login = generate_random_string(10)
        self.password = generate_random_string(10)
        self.first_name = generate_random_string(10)
        payload = {
            "login": self.login,
            "password": self.password,
            "firstName": self.first_name,
        }

        response = requests.post(f"{urls.BASE_URL}/api/v1/courier", json=payload)

        assert response.status_code == 201
        assert response.json()["ok"] is True

    @allure.title("Создание курьера с существующим логином")
    @allure.description("Повторное использование логина возвращает ошибку")
    def test_create_courier_exist_login_negative(self):
        courier = register_new_courier_and_return_login_password()
        self.login = courier[0]
        self.password = courier[1]
        self.first_name = courier[2]

        datacourier = {
            "login": self.login,
            "password": self.password,
            "firstName": self.first_name,
        }

        response = requests.post(f"{urls.BASE_URL}/api/v1/courier", json=datacourier)

        assert response.status_code == 409
        assert (
            response.json()["message"]
            == "Этот логин уже используется. Попробуйте другой."
        )

    @allure.title("Создание курьера без обязательного поля: {param_id}")
    @allure.description("Создание без логина или пароля возвращает ошибку")
    @pytest.mark.parametrize(
        "payload",
        [
            pytest.param({"password": "pass1", "firstName": "Name1"}, id="no_login"),
            pytest.param({"login": "log1", "firstName": "Name1"}, id="no_password"),
        ],
    )
    def test_create_courier_without_login_or_password_negative(self, payload):
        response = requests.post(f"{urls.BASE_URL}/api/v1/courier", json=payload)

        assert response.status_code == 400
        assert (
            response.json()["message"]
            == "Недостаточно данных для создания учетной записи"
        )


class TestLoginCourierApi(BaseCourierApi):
    @allure.title("Вход курьера")
    @allure.description("Зарегистрированный курьер может залогиниться")
    def test_login_courier(self):
        courier = register_new_courier_and_return_login_password()
        self.login = courier[0]
        self.password = courier[1]

        datacourier = {"login": self.login, "password": self.password}

        response = requests.post(
            f"{urls.BASE_URL}/api/v1/courier/login", json=datacourier
        )

        assert response.status_code == 200
        assert "id" in response.json()

    @allure.title("Вход несуществующего курьера")
    @allure.description("Вход с несуществующими данными возвращает ошибку")
    def test_login_courier_not_exist_negative(self):
        datacourier = {
            "login": generate_random_string(20),
            "password": generate_random_string(20),
        }

        response = requests.post(
            f"{urls.BASE_URL}/api/v1/courier/login", json=datacourier
        )

        assert response.status_code == 404
        assert response.json()["message"] == "Учетная запись не найдена"

    @allure.title("Вход курьера без обязательного поля: {param_id}")
    @allure.description("Вход без логина или пароля возвращает ошибку")
    @pytest.mark.parametrize("login, password", [["login", ""], ["", "password"]])
    def test_login_courier_without_login_or_password_negative(self, login, password):
        datacourier = {"login": login, "password": password}

        response = requests.post(
            f"{urls.BASE_URL}/api/v1/courier/login", json=datacourier
        )

        assert response.status_code == 400
        assert response.json()["message"] == "Недостаточно данных для входа"
