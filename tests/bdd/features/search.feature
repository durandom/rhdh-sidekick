Feature: Search Command
  As a user of the sidekick CLI
  I want to search for data using a query string
  So that I can find relevant information quickly

  Scenario: Search with a query that finds results
    Given I have the sidekick CLI installed
    When I run the command "sidekick search search python"
    Then I should see "Found 1 results for 'python'"
    And I should see "Python programming tutorial"

  Scenario: Search with a query that finds no results
    Given I have the sidekick CLI installed
    When I run the command "sidekick search search nonexistent"
    Then I should see "No results found for 'nonexistent'"
