import typing
from enum import Enum, auto

from behave import *
from behave.runner import Context

from ovoclient.models import TransactionType, PaymentRequest, AppSource, TransactionRequest


class SimulationType(Enum):
    request = 'request'
    response = 'response'


SIMULATED_JSON = {
    '/pos': {
        SimulationType.response: {
            "type": "0210",
            "processingCode": "040000",
            "amount": 950000,
            "date": "2017-11-03 00:35:03.249",
            "traceNumber": 3451,
            "hostTime": "003503",
            "hostDate": "1103",
            "referenceNumber": 123412,
            "approvalCode": "410315",
            "responseCode": "00",
            "tid": "00300001",
            "mid": "0010000000MM001",
            "transactionRequestData": {
                "merchantInvoice": "MM001-2017-10-29-213",
                "batchNo": "000004",
                "phone": "081296010400"
            },
            "transactionResponseData": {
                "storeAddress1": "rasuna",
                "ovoid": "********0400",
                "cashUsed": "0",
                "storeAddress2": "Said",
                "ovoPointsEarned": "0",
                "cashBalance": "0",
                "fullName": "andrey angkoso",
                "storeName": "MatahariMall HeadQuarter",
                "ovoPointsUsed": "950000",
                "ovoPointsBalance": "2130700",
                "storeCode": "MM001",
                "paymentType": "PUSH TO PAY"
            }
        }
    }
}


@given('a simulated response from {endpoint}')
def step_impl(context: Context, endpoint: str) -> None:
    try:
        context.simulated_json = SIMULATED_JSON[endpoint][SimulationType.response]
    except KeyError:
        raise RuntimeError(f'Misconfigured test: No simulated responses for "{endpoint}"')


@when("I serialize the object")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.serialized = context.entity.serialize()


class PaymentRequestExample:
    DATA_MAP = {
        'success': {
            SimulationType.request: {
                'transaction_type': TransactionType.PUSH_TO_PAY,
                'amount': 95000,
                'date': '2019-01-01 00:00:00',
                'reference_number': '0023902',
                'tid': '12323',
                'mid': '0010000000MM001',
                'merchant_id': 'MID123445',
                'store_code': 'STORE01',
                'app_source': AppSource.EDC,
                'transaction_request_data': TransactionRequest(
                    batch_no='000004',
                    phone='091029302',
                    merchant_invoice='INV-0010232'
                )
            },
            SimulationType.response: {
                "type": "0210",
                "processingCode": "040000",
                "amount": 950000,
                "date": "2019-01-01 00:00:00",
                "traceNumber": 3451,
                "hostTime": "003503",
                "hostDate": "1103",
                "referenceNumber": '0023902',
                "approvalCode": "410315",
                "responseCode": "00",
                "tid": "12323",
                "mid": "0010000000MM001",
                "transactionRequestData": {
                    "merchantInvoice": "INV-0010232",
                    "batchNo": "000004",
                    "phone": "091029302"
                },
                "transactionResponseData": {
                    "storeAddress1": "rasuna",
                    "ovoid": "********0400",
                    "cashUsed": "0",
                    "storeAddress2": "Said",
                    "ovoPointsEarned": "0",
                    "cashBalance": "0",
                    "fullName": "andrey angkoso",
                    "storeName": "MatahariMall HeadQuarter",
                    "ovoPointsUsed": "950000",
                    "ovoPointsBalance": "2130700",
                    "storeCode": "MM001",
                    "paymentType": "PUSH TO PAY"
                }

            }
        }
    }

    def get_examples(self, input) -> typing.Dict:
        return self.DATA_MAP.get(input)


@given('a PaymentRequest for request = "{request}"')
def step_impl(context, request):
    """
    :param request:
    :type context: behave.runner.Context
    """
    context.examples = PaymentRequestExample().get_examples(request)
    context.example_request = context.examples.get(SimulationType.request)
    context.example_response = context.examples.get(SimulationType.response)
    context.entity = PaymentRequest(**context.example_request)

