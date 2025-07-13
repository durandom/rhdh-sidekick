Feature: CLI Help Output
  As a user of the sidekick CLI
  I want to see help information when I run the help command
  So that I can understand how to use the application

  Scenario: Display help information for main command
    Given I have the sidekick CLI installed
    When I run the command "sidekick --help"
    Then I should see "Usage: root"
