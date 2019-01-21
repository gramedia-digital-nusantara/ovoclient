"""
Gateway
=======

This module is the primary class for communicating with the AkuLaku API.
"""
from datetime import datetime
import hashlib
import hmac
import logging
from http import HTTPStatus

import requests

from ovoclient.exceptions import OvoClientError
from ovoclient.models import PaymentRequest, PaymentResponse, TransactionType

log = logging.getLogger('ovoclient')

__all__ = ['OvoClientGateway', ]


class OvoClientGateway:
    def __init__(self, app_id, secret_key, use_sandbox=False):
        self.app_id = app_id
        self.secret_key = secret_key
        self.use_sandbox = use_sandbox

    @property
    def base_url(self):
        """ Get base URL for the gateway
        """
        return "https://api.byte-stack.net" if self.use_sandbox \
            else "https://api.ovo.id"

    def generate_signature(self, random: int):
        return hmac.new(f'{self.app_id}{random}'.encode(), self.secret_key.encode(), hashlib.sha256)

    def send_request(self, request_data, random_number):
        data = request_data.serialize()

        headers = {
            'app-id': self.app_id,
            'Random': random_number,
            'Hmac': self.generate_signature(random_number).digest()
        }
        try:
            url = f'{self.base_url}/pos'
            response = requests.post(url=url, headers=headers, data=data)
            if response.status_code != HTTPStatus.OK:
                raise Exception

            response_data = PaymentResponse.from_api_json(response.json())

            if not response_data.is_success:
                raise OvoClientError(response_data.response_status)

            return response_data
        except Exception as exc:
            log.exception(f"Failed to create new ovo payment for order {request_data.reference_number}")
            raise

    def create_payment(self, payment_request):
        """Send push to pay transaction

        :param `ovoclient.models.PaymentRequest payment_request:
        :return:
        """
        if payment_request.transaction_type != TransactionType.PUSH_TO_PAY:
            raise OvoClientError('Invalid Transaction type')
        random_number = int(datetime.now().timestamp())
        return self.send_request(payment_request, random_number)

    def reverse_payment(self, reverse_request:PaymentRequest):
        if reverse_request.transaction_type != TransactionType.REVERSAL:
            raise OvoClientError('Invalid Transaction type')
        random_number = int(datetime.now().timestamp())
        return self.send_request(reverse_request, random_number)

    def void_payment(self, void_request:PaymentRequest):
        if void_request.transaction_type != TransactionType.VOID:
            raise OvoClientError('Invalid Transaction type')
        random_number = int(datetime.now().timestamp())

        return self.send_request(void_request, random_number)

