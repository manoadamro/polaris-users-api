Feature: User management
  As a admin
  I want to create a clinician
  So that I can manage patient care

  Background:
    Given a valid JWT
    Given RabbitMQ is running

  Scenario: Clinician is created and updated
    Given a SEND clinician with email john.wick@hitman.com exists
      And a CLINICIAN_CREATED_MESSAGE message is published to RabbitMQ
      And a EMAIL_NOTIFICATION_MESSAGE message is published to RabbitMQ
    Then the clinician john.wick@hitman.com can be found by email
    When we patch the clinician john.wick@hitman.com
    Then the response matches clinician_output_1.json
      And a CLINICIAN_UPDATED_MESSAGE message is published to RabbitMQ

  Scenario: Deactivate clinician
    Given a SEND clinician with email viggo.tarasov@hitman.com exists
      And a CLINICIAN_CREATED_MESSAGE message is published to RabbitMQ
      And a EMAIL_NOTIFICATION_MESSAGE message is published to RabbitMQ
    When we deactivate the clinician viggo.tarasov@hitman.com
    Then the clinician is not active
      And a CLINICIAN_UPDATED_MESSAGE message is published to RabbitMQ
      And a AUDIT_MESSAGE message is published to RabbitMQ

  Scenario: Get clinician by id
    Given a SEND clinician with email iosef.tarasov@hitman.com exists
      And a CLINICIAN_CREATED_MESSAGE message is published to RabbitMQ
      And a EMAIL_NOTIFICATION_MESSAGE message is published to RabbitMQ
    When we patch the clinician iosef.tarasov@hitman.com
      And a CLINICIAN_UPDATED_MESSAGE message is published to RabbitMQ
      And we get the clinician by UUID
    Then the response matches clinician_output_2.json

  Scenario: Get clinicians by location
    When I create 2 clinicians in bulk with location A1
    When we get the clinicians for location A1
    Then the response is the expected list of clinicians

  Scenario: Clinician accepts terms agreement
    Given a SEND clinician with email adrianne.palicki@hitman.com exists
      And a CLINICIAN_CREATED_MESSAGE message is published to RabbitMQ
      And a EMAIL_NOTIFICATION_MESSAGE message is published to RabbitMQ
  When adrianne.palicki@hitman.com accepts the terms agreement
  Then adrianne.palicki@hitman.com has a terms agreement that matches terms_agreement.json

  Scenario: Change clinician password by email
    Given a SEND clinician with email hotel.manager@hitman.com exists
      And a CLINICIAN_CREATED_MESSAGE message is published to RabbitMQ
      And a EMAIL_NOTIFICATION_MESSAGE message is published to RabbitMQ
    When clinician with email hotel.manager@hitman.com changes password to SillyPassword-2
      and acting as a login user 
    Then clinician with email hotel.manager@hitman.com can login with password SillyPassword-2
      And a AUDIT_MESSAGE message is published to RabbitMQ

  Scenario: Clinician is created and location deleted
    Given a SEND clinician with email oksana.astankova@hitman.com exists
      And a CLINICIAN_CREATED_MESSAGE message is published to RabbitMQ
      And a EMAIL_NOTIFICATION_MESSAGE message is published to RabbitMQ
    When we delete a location on the clinician oksana.astankova@hitman.com
    Then the locations response matches clinician_output_1.json
      And a CLINICIAN_UPDATED_MESSAGE message is published to RabbitMQ


  Scenario: Create clinician location bookmark
    Given a SEND clinician with email anton.chigurh@hitman.com exists
      And a CLINICIAN_CREATED_MESSAGE message is published to RabbitMQ
      And a EMAIL_NOTIFICATION_MESSAGE message is published to RabbitMQ
    When we add a clinician location bookmark for anton.chigurh@hitman.com
    Then the clinician anton.chigurh@hitman.com can be found by email
    Then the response includes a location bookmark

  Scenario: Delete clinician location bookmark
    Given a SEND clinician with email pete.waterman@hitman.com exists
      And a CLINICIAN_CREATED_MESSAGE message is published to RabbitMQ
      And a EMAIL_NOTIFICATION_MESSAGE message is published to RabbitMQ
    When we add a clinician location bookmark for pete.waterman@hitman.com
    Then the clinician pete.waterman@hitman.com can be found by email
    When we delete a clinician location bookmark for pete.waterman@hitman.com
    Then the clinician pete.waterman@hitman.com can be found by email
    Then the response does not include a location bookmark
