# Created by heri at 17/01/2019
Feature: Request Serialization
  Verify the request data that we are sending on to the API

  Scenario: TransactionRequest serialization
    Given a TransactionRequest with batch_no = {batch_no}, phone = {phone}, merchant_invoice = {merchant_invoice}
    When I serialize the object
    Then the TransactionRequest is converted to dictionary correctly

  Scenario Outline: PaymentRequest serialization
    Given a PaymentRequest for request = "<request>"
    When I serialize the object
    Then the PaymentRequest is serialized correctly
    Examples:
      | request | response |
      | success | success  |

