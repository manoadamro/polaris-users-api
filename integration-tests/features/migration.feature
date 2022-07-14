Feature: Data migration
  Clinician migration
  As a software engineer
  I want to migrate clinicians to the users-api
  So that I can move off Neo4J

  Background:
    Given a valid JWT
    Given RabbitMQ is running

  Scenario: Clinicians can be created in bulk
    When I create 100 clinicians in bulk with location A1
    Then I see that the clinicians have been created
