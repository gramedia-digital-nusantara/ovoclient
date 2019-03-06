from http import HTTPStatus
from unittest.mock import MagicMock

from behave import given, when
from behave.runner import Context
from requests import Response

from ovoclient.gateway import OvoClientGateway
from ovoclient.models import PaymentRequest


@given('a production API client')
def step_impl(context: Context) -> None:
    context.client = OvoClientGateway(
        app_id='app_id',
        secret_key='secret_key',
        use_sandbox=True
    )

@when("I perform book delivery")
def step_impl(context):
    client: OvoClientGateway = context.client

    mock = MagicMock(spec=Response)
    mock.json = lambda: context.simulated_json

    context.requests_mock.post.return_value = mock
    context.requests_mock.post.return_value.status_code = HTTPStatus.OK

    context.response = client.create_payment(
        PaymentRequest(
            transaction_type='merchant order id',
            service_type=ServiceType.same_day,
            packages=[],
            cash_on_delivery=CashOnDelivery(amount=0),
            sender=Sender(first_name='first',
                          last_name='last',
                          title='employee',
                          company_name='company',
                          email='first@last.company',
                          phone='phone',
                          sms_enabled=True,
                          instruction=''),
            recipient=Recipient(first_name='first',
                                last_name='last',
                                title='employee',
                                company_name='company',
                                email='first@last.company',
                                phone='phone',
                                sms_enabled=True,
                                instruction=''),
            origin=Origin(address='Full address of origin',
                          keywords='Extra keywords',
                          coordinates=Coordinates(latitude=1.1, longitude=1.2)),
            destination=Destination(address='Full address of customer',
                                    keywords='Extra keywords',
                                    coordinates=Coordinates(latitude=1.1, longitude=1.2))
        )
    )