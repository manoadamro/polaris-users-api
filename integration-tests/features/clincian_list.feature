Feature: User management
  As a admin
  I want to view clinicians
  So that I can manage my users

  Background:
    Given a valid JWT
    And RabbitMQ is running

  Scenario: View clinician list (v1)
    Given I create 20 SEND clinicians
    When I get a list of all clinicians (v1)
    Then I can see the expected clinicians (v1)

  Scenario: View clinician list (v2)
    Given I create 20 SEND clinicians
    When I get a list of all clinicians (v2)
    Then I can see the expected clinicians (v2)

  Scenario: Search clinicians
    Given I create 20 SEND clinicians
    And a SEND clinician with email john.wick@hitman.com exists
    When I search clinicians using the term 'wick'
    Then I can see the clinician with email john.wick@hitman.com
