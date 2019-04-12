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
from ovoclient.models import PaymentRequest, PaymentResponse, ResponseCode

log = logging.getLogger('ovoclient')

__all__ = ['OvoClientGateway', ]

CHARGE_DEFAULT_TIMEOUT = 65
REVERSAL_DEFAULT_TIMEOUT = 15
MAX_REVERSAL_COUNT = 3


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

    def charge(self, payment_request: PaymentRequest, timeout: int = None):
        """Send push to pay transaction (CHARGE)

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
                                     timeout=CHARGE_DEFAULT_TIMEOUT if not timeout else timeout)
            response_json = json.loads(response.content.decode('utf-8')) if response.content else {}
            if response.status_code == HTTPStatus.NOT_FOUND and not response_json:
                response_json = data
                response_json['responseCode'] = ResponseCode.NOT_FOUND.value
                log.exception(f"Failed to create new ovo payment for order {payment_request.reference_number}")

            if response.status_code not in [HTTPStatus.OK, HTTPStatus.NOT_FOUND] and not response_json:
                raise OvoClientError("Failed to register into ovo api")

        except (requests.ConnectTimeout, requests.HTTPError, requests.ConnectionError):
            response_json = data
            log.exception(f"Failed to create new ovo payment for order {payment_request.reference_number}")
        transaction_request_data = data.get('transactionRequestData', {})
        response_json['transactionRequestData']['phone'] = transaction_request_data.get('phone', '')
        response_json['transactionRequestData']['merchantInvoice'] = transaction_request_data.get('merchantInvoice',
                                                                                                  '')
        return PaymentResponse.from_api_json(response_json)

    def reversal(self, payment_request: PaymentRequest, timeout: int = None, attempt: int = 0):
        """Send push to pay transaction (REVERSE)

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
            attempt += 1
            response = requests.post(url=url,
                                     data=json.dumps(data),
                                     headers=headers,
                                     timeout=REVERSAL_DEFAULT_TIMEOUT if not timeout else timeout)
            response_json = json.loads(response.content.decode('utf-8')) if response.content else {}
            if response.status_code == HTTPStatus.NOT_FOUND and not response_json:
                response_json = data
                response_json['responseCode'] = ResponseCode.NOT_FOUND.value
                log.exception(f"Failed to create reversal for order {payment_request.reference_number}")

            if response.status_code != HTTPStatus.OK and not response_json:
                raise OvoClientError("Failed to register into ovo api")

        except (requests.ConnectTimeout, requests.HTTPError, requests.ConnectionError, requests.ReadTimeout):
            response_json = data
            log.exception(f"Failed to create new ovo reversal for order {payment_request.reference_number}")
        transaction_request_data = data.get('transactionRequestData', {})
        response_json['transactionRequestData']['phone'] = transaction_request_data.get('phone', '')
        response_json['transactionRequestData']['merchantInvoice'] = transaction_request_data.get('merchantInvoice',
                                                                                                  '')
        return PaymentResponse.from_api_json(response_json), attempt

    def recursive_reversal(self, payment_request: PaymentRequest, timeout: int = None):
        """
        Recursive reversal based on MAX_REVERSAL_COUNT and response from reversal whether its succeeded
        :param payment_request:
        :param timeout:
        :return:
        """
        attempt = 0
        response_json = None
        while attempt < MAX_REVERSAL_COUNT and (
                not response_json or
                response_json.response_code != ResponseCode.SUCCESS.value
        ):
            payment_request.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            response_json, attempt = self.reversal(payment_request=payment_request, timeout=timeout, attempt=attempt)
        return response_json
