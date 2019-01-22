import hashlib
from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from behave import *
from requests import Response
from ovoclient.gateway import OvoClientGateway


@given("a gateway with app id of {app_id}, secret key of {secret_key}, sandbox is {sandbox}")
def step_impl(context, app_id, secret_key, sandbox):
    context.app_id = app_id
    context.secret_key = secret_key
    context.gateway = OvoClientGateway(
        app_id=app_id,
        secret_key=secret_key,
        use_sandbox=(True if sandbox == "True" else False)
    )


@when("i check base url")
def step_impl(context):
    context.base_url = context.gateway.base_url


@then('i get url "{url}"')
def step_impl(context, url):
    assert context.base_url == url


@when("I make a send request")
def step_impl(context):
    mock_post = MagicMock(spec=Response)
    mock_post.status_code = HTTPStatus.OK
    mock_post.json.return_value = context.example_response

    patcher = patch('ovoclient.gateway.requests')
    fake_requests = patcher.start()
    fake_requests.post.return_value = mock_post

    context.json_value = mock_post.json.return_value
    context.random_number = int(datetime.now().timestamp())
    context.response_order_id = context.gateway.send_request(
        context.entity, random_number=context.random_number
    )
    context.request = fake_requests.post.call_args[1]

    patcher.stop()


@then("the Header is generated correctly")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    import hmac
    hmacx = hmac.new(f'{context.app_id}{context.random_number}'.encode(), context.secret_key.encode(), hashlib.sha256)

    assert context.request['headers']['Hmac'] == hmacx.digest()
