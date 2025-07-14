Feature: Search Command
  As a user of the sidekick CLI
  I want to search for data using a query string
  So that I can find relevant information quickly

  Scenario: Search with a query that finds results
    Given I have the sidekick CLI installed
    When I run the command "sidekick search python"
    Then the command should execute successfully
    And I should see search output

  Scenario: Search with a query that finds no results
    Given I have the sidekick CLI installed
    When I run the command "sidekick search nonexistent"
    Then the command should execute successfully
    And I should see search output
