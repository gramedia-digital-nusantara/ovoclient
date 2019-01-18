

Feature: JSON response parsing
  Scenario: TransactionRequest from api json
    Given a simulated response from /pos
    When I process the response
    Then the response is converted to TransactionRequest object