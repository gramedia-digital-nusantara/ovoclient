"""
Gateway
=======

This module is the primary class for communicating with the AkuLaku API.
"""
import base64
from datetime import datetime
import hashlib
import hmac
import json
import logging
from http import HTTPStatus

import requests

from ovoclient.exceptions import OvoClientError
from ovoclient.models import PaymentRequest, PaymentResponse

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
        hmac_signature = hmac.new(f'{self.app_id}{random}'.encode(),
                                  self.secret_key.encode(), hashlib.sha256).digest()
        return base64.b64encode(hmac_signature).decode()

    def create_payment(self, payment_request: PaymentRequest):
        """Send push to pay transaction

        :param `ovoclient.models.PaymentRequest payment_request:
        :return:
        """
        data = payment_request.serialize()
        random_number = int(datetime.now().timestamp())

        headers = {
            'app-id': self.app_id,
            'Random': f"{random_number}",
            'Hmac': self.generate_signature(random_number),
            'Content-Type': 'application/json'
        }
        try:
            url = f'{self.base_url}/pos'
            response = requests.post(url=url,
                                     data=json.dumps(data),
                                     headers=headers,
                                     timeout=60)
            response_json = json.loads(response.content.decode('utf-8')) if response.content else {}
            if response.status_code != HTTPStatus.OK and not response_json:
                raise OvoClientError("Failed to register into ovo api")

        except (requests.ConnectTimeout, requests.HTTPError, requests.ConnectionError):
            response_json = data
            log.exception(f"Failed to create new ovo payment for order {payment_request.reference_number}")
        except OvoClientError as exc:
            raise exc
        transaction_request_data = data.get('transactionRequestData', {})
        response_json['transactionRequestData']['phone'] = transaction_request_data.get('phone', '')
        response_json['transactionRequestData']['merchantInvoice'] = transaction_request_data.get('merchantInvoice',
                                                                                                  '')

        return PaymentResponse.from_api_json(response_json)