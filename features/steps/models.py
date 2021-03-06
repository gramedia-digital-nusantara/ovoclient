from behave import *
from ovoclient.models import TransactionRequest, AppSource


@given("a TransactionRequest with batch_no = {batch_no}, phone = {phone}, merchant_invoice = {merchant_invoice}")
def step_impl(context, batch_no, phone, merchant_invoice):
    """
    :type batch_no: str
    :type phone: str
    :type merchant_invoice: str
    :type context: behave.runner.Context
    """
    context.entity = TransactionRequest(
        batch_no=batch_no,
        phone=phone,
        merchant_invoice=merchant_invoice
    )


@then("the TransactionRequest is converted to dictionary correctly")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert context.serialized == {
        'batchNo': context.entity.batch_no,
        'phone': context.entity.phone,
        'merchantInvoice': context.entity.merchant_invoice
    }


@when("I process the response")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.entity = TransactionRequest.from_api_json(context.simulated_json.get('transactionRequestData'))


@then("the response is converted to TransactionRequest object")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert isinstance(context.entity, TransactionRequest)
    assert context.entity.batch_no == context.simulated_json.get('transactionRequestData').get('batchNo')


@then("the PaymentRequest is serialized correctly")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    request_type, processing_code, description = context.examples.get('transaction_type').value

    assert context.entity.request_type == request_type
    assert context.entity.processing_code == processing_code
    assert context.serialized == {
        'type': request_type,
        'processingCode': processing_code,
        'amount': 50000,
        'date': '2019-01-01 00:00:00',
        'referenceNumber': '0023902',
        'tid': '12323',
        'mid': 'mid',
        'merchantId': 'MID123445',
        'storeCode': 'STORE01',
        'appSource': AppSource.EDC.value,
        'transactionRequestData': {
            'batchNo': 'BATCH1',
            'phone': '091029302',
            'merchantInvoice': 'INV-0010232'
        }
    }

