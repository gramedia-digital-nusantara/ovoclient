# Created by heri at 21/01/2019
Feature: OVO Client API Gateway
  # Enter feature description here
  Scenario: Base URL for Sandbox API
    Given a gateway with app id of 123, secret key of s3cret, sandbox is True
    When i check base url
    Then i get url "https://api.byte-stack.net"

  Scenario: Base URL for Production API
    Given a gateway with app id of 123, secret key of s3cret, sandbox is False
    When i check base url
    Then i get url "https://api.ovo.id"

  Scenario Outline: Generate send request
    Given a gateway with app id of 123, secret key of s3cret, sandbox is True
    And a PaymentRequest for request = "<request>"
    When I make a send request
    Then the Header is generated correctly
    Examples:
      | request | response |
      | success | success  |
