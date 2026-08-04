from flask import current_app

from app import db
from app.models import CabecerasPresupuestos, PagosElectronicos
from app.pagos_electronicos.cliente import ClienteMercadoPago
import datetime

import json


class PagoElectronicoService:
    @staticmethod
    def _cliente():
        return ClienteMercadoPago(
            access_token=current_app.config["MP_ACCESS_TOKEN"],
            external_pos_id=current_app.config["MP_EXTERNAL_POS_ID"]
        )
    
    @staticmethod
    def crear_pago(id_cabecera):

        cabecera = CabecerasPresupuestos.get_by_id(id_cabecera)

        if not cabecera:
            raise Exception("No existe la cabecera del presupuesto.")

        pago = PagosElectronicos()

        pago.id_cabecera_presupuesto = cabecera.id
        pago.external_reference = str(cabecera.id)
        pago.importe = cabecera.importe_total
        pago.estado = "CREANDO"

        try:

            pago.add()

            respuesta = PagoElectronicoService._cliente().crear_order(
                external_reference=pago.external_reference,
                title=f"Venta {cabecera.id}",
                amount=float(cabecera.importe_total)
            )

            pago.respuesta_api = json.dumps(
                respuesta,
                ensure_ascii=False,
                indent=2
            )

            if respuesta.get("ok"):
                
                data = respuesta["data"]

                pago.order_id = data["id"]

                payments = data.get("transactions", {}).get("payments", [])

                if payments:
                    pago.payment_id = payments[0]["id"]
                   

                pago.estado = data.get("status", "DESCONOCIDO")
                pago.estado_detalle = data.get("status", "DESCONOCIDO")

                created_date = data.get("created_date")
                if created_date:
                    pago.fecha_creacion_api = datetime.datetime.fromisoformat(
                        created_date.replace("Z", "+00:00")
                    )

            else:

                pago.estado = "ERROR"

            db.session.commit()

            return pago

        except Exception:

            db.session.rollback()
            raise
    
    @staticmethod
    def consultar_order(order_id):

        return PagoElectronicoService._cliente().consultar_order(order_id)
    
    @staticmethod
    def sincronizar_order(order_id):
        pago = PagosElectronicos.get_by_order_id(order_id)
        
        if not pago:
            return {
                "ok": False,
                "error": "Pago electrónico inexistente."
            }

        order = PagoElectronicoService.consultar_order(
            pago.order_id
        )
        #valido que conecte y me devuelva un json
        if not order.get("ok"):
            pago.estado = "ERROR_CONSULTA_ORDER"
            pago.save()

            return order

        order_data=order.get('data',{})
        payments=order_data.get('transactions', {}).get('payments', [])
        
        #valido que exista un payment
        if not payments:
            pago.estado = order_data.get("status")
            pago.estado_detalle = order_data.get("status_detail")
            pago.save()
            return order
        
        reference_id = payments[0].get('reference_id')
        
        payment = PagoElectronicoService.consultar_payment(
            reference_id
        )
        pago.respuesta_api = json.dumps(
                    order,
                    ensure_ascii=False,
                    indent=2
                )
        
        if not payment.get("ok"):
            pago.estado = order_data.get("status")
            pago.estado_detalle = order_data.get("status_detail")
            pago.save()
            return order

        payment_data=payment.get('data',{})
        payer=payment_data.get('payer',{})
        

        fecha = payment_data.get("date_approved")

        if fecha:
            pago.fecha_aprobacion = datetime.datetime.fromisoformat(
                fecha.replace("Z", "+00:00")
            )

        pago.estado=order_data.get('status')
        pago.estado_detalle = order_data.get("status_detail")
        pago.payer_email=payer.get('email')
        pago.first_name=payer.get('first_name')
        pago.last_name=payer.get('last_name')
        pago.medio_pago=payment_data.get('payment_method_id')
        pago.tipo_medio_pago=payment_data.get('payment_type_id')
        pago.reference_id = reference_id

        pago.respuesta_payment_api = json.dumps(
                            payment,
                            ensure_ascii=False,
                            indent=2
                        )
        pago.save()
        return order
        
            

    @staticmethod
    def consultar_payment(reference_id):

        return PagoElectronicoService._cliente().consultar_payment(reference_id)
    
    @staticmethod
    def actualizar_payment(reference_id):
        pago = PagosElectronicos.get_by_order_id(reference_id)
        
        if not pago:
            return False

        respuesta = PagoElectronicoService.consultar_pago(
            pago.order_id
        )

        #
        # actualizar estado
        #

        return respuesta