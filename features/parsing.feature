

Feature: JSON response parsing
  Scenario: TransactionRequest from api json
    Given a simulated response from /pos
    When I process the response
    Then the response is converted to TransactionRequest object

  Scenario Outline: PaymentResponse from api json
    Given a PaymentRequest for request = "<request>"
    When I process the request
    Then the response is converted to PaymentRequest
    Examples:
      | request | response |
      | success | success  |