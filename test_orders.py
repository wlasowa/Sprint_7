import requests
import pytest
import allure
import urls


class TestCreateOrderApi:
    def setup_method(self):
        self.track = None

    @allure.title("Создание заказа с цветом: {color}")
    @allure.description("Проверка создания заказа с разными вариантами цвета")
    @pytest.mark.parametrize(
        "color",
        [
            pytest.param(["BLACK"], id="BLACK"),
            pytest.param(["GREY"], id="GREY"),
            pytest.param(["BLACK", "GREY"], id="BLACK_GREY"),
            pytest.param([], id="no_color"),
        ],
    )
    def test_create_order_with_different_colors(self, color):
        dataorder = {
            "firstName": "Sasha",
            "lastName": "Vlasova",
            "address": "Moscow, 77 apt.",
            "metroStation": 7,
            "phone": "+79995424141",
            "rentTime": 3,
            "deliveryDate": "2026-11-29",
            "comment": "Saske, come back to Konoha",
            "color": color,
        }
        response = requests.post(f"{urls.BASE_URL}/api/v1/orders", json=dataorder)
        self.track = response.json()["track"]

        assert response.status_code == 201
        assert "track" in response.json()

    def teardown_method(self):
        if self.track is not None:
            self.cancel_order()

    @allure.step("Отменить заказ после теста")
    def cancel_order(self):
        cancel_response = requests.put(
            f"{urls.BASE_URL}/api/v1/orders/cancel", params={"track": self.track}
        )
        assert cancel_response.status_code == 200


class TestGetOrdersApi:
    @allure.title("Получение списка заказов")
    @allure.description("Проверка ответа при запросе списка заказов")
    def test_get_orders_list(self):
        response = requests.get(f"{urls.BASE_URL}/api/v1/orders")

        assert response.status_code == 200
        assert "orders" in response.json()

    @allure.title("Получение заказов несуществующего курьера")
    @allure.description("Запрос с несуществующим ID курьера возвращает ошибку")
    def test_get_orders_list_negative(self):
        courier_id = -1
        params = {"courierId": courier_id}
        response = requests.get(f"{urls.BASE_URL}/api/v1/orders", params=params)

        assert response.status_code == 404
        assert (
            response.json()["message"]
            == f"Курьер с идентификатором {courier_id} не найден"
        )
