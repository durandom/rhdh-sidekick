Feature: Research Command
  As a user of the sidekick CLI
  I want to research a topic
  So that I get a research report on that topic

  Scenario: Search with a topic that generates a report
    Given I have the sidekick CLI installed
    When I run the command "sidekick research 'what is the best pizza dough'"
    Then the command should execute successfully
    And I should see a research report output

  Scenario: Search with a topic and save to file
    Given I have the sidekick CLI installed
    When I run the command "sidekick research --output pizza.md 'what is the best pizza dough'"
    Then the command should execute successfully
    And I should see a research report output
    And I should have a file containing the same output
    And I should have a file called 'pizza.md'
