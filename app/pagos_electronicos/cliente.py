import requests
import uuid


class ClienteMercadoPago:
    """
    Cliente para consumir la API REST de Mercado Pago.

    Esta clase NO conoce Flask, SQLAlchemy ni los modelos de la aplicación.
    Solamente encapsula las llamadas HTTP.
    """

    BASE_URL = "https://api.mercadopago.com"

    def __init__(
        self,
        access_token,
        external_pos_id):

        self.access_token = access_token
        self.external_pos_id = external_pos_id

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    # ------------------------------------------------------------------
    # Método interno para todas las llamadas HTTP
    # ------------------------------------------------------------------

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:

        headers = kwargs.pop("headers", self.headers)

        try:
 
            response = requests.request(
                method=method,
                url=f"{self.BASE_URL}{endpoint}",
                headers=headers,
                timeout=20,
                **kwargs
            )

            try:
                body = response.json()
            except Exception:
                body = response.text

            return {
                "ok": response.ok,
                "status_code": response.status_code,
                "data": body
            }

        except requests.exceptions.Timeout:

            return {
                "ok": False,
                "status_code": None,
                "error": "Timeout al conectar con Mercado Pago"
            }

        except requests.exceptions.ConnectionError:

            return {
                "ok": False,
                "status_code": None,
                "error": "No fue posible conectar con Mercado Pago"
            }

        except Exception as ex:

            return {
                "ok": False,
                "status_code": None,
                "error": str(ex)
            }

    # ------------------------------------------------------------------
    # STORE
    # ------------------------------------------------------------------

    def obtener_stores(self):

        return self._request(
            "GET",
            "/users/me/stores"
        )

    # ------------------------------------------------------------------
    # POS
    # ------------------------------------------------------------------

    def obtener_pos(self):

        return self._request(
            "GET",
            "/pos"
        )
    # ------------------------------------------------------------------
    # ORDER
    # ------------------------------------------------------------------

    def crear_order(
        self,
        external_reference,
        title,
        amount):

        headers = self.headers.copy()

        headers["X-Idempotency-Key"] = str(uuid.uuid4())

        payload = {

                "type": "qr",

                "total_amount": f"{amount:.2f}",

                "description": title,

                "external_reference": external_reference,

                "expiration_time": "PT15M",

                "config": {
                    "qr": {
                        "external_pos_id": self.external_pos_id,
                        "mode": "static"
                    }
                },

                "transactions": {
                    "payments": [
                        {
                            "amount": f"{amount:.2f}"
                        }
                    ]
                },

                "items": [
                    {
                        "title": title,
                        "unit_price": f"{amount:.2f}",
                        "quantity": 1,
                        "unit_measure": "unit"
                    }
                ]
            }
        
        return self._request(
            "POST",
            "/v1/orders",
            headers=headers,
            json=payload
        )

    # ------------------------------------------------------------------
    # CONSULTAR ORDER
    # ------------------------------------------------------------------
    def consultar_order(self, order_id):

        return self._request(
            "GET",
            f"/v1/orders/{order_id}"

        )

    # ------------------------------------------------------------------
    # PAYMENT
    # ------------------------------------------------------------------

    def consultar_payment(self, reference_id):

        return self._request(
            "GET",
            f"/v1/payments/{reference_id}"
        )

    # ------------------------------------------------------------------
    # CANCELAR ORDER
    # ------------------------------------------------------------------

    def cancelar_order(self, order_id):

        return self._request(
            "DELETE",
            f"/merchant_orders/{order_id}"
        )