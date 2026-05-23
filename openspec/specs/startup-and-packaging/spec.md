## ADDED Requirements

### Requirement: Persist memo data locally
The system SHALL persist memo events, reminder rules, reminder state, and holiday cache data in a local SQLite database so that scheduling data remains available across application restarts.

#### Scenario: Reload persisted events on startup
- **WHEN** the application starts after one or more events were previously saved
- **THEN** the system loads those events and their reminder state from the local database

### Requirement: Configure Windows startup launch
The system SHALL allow the user to enable or disable automatic launch at Windows sign-in.

#### Scenario: Enable startup launch
- **WHEN** the user enables the startup launch option
- **THEN** the system registers the application to start automatically when the current Windows user signs in

#### Scenario: Disable startup launch
- **WHEN** the user disables the startup launch option
- **THEN** the system removes the application's automatic startup registration for the current Windows user

### Requirement: Produce Windows distributable build
The system SHALL support building the application into a Windows distributable executable using PyInstaller.

#### Scenario: Build packaged application
- **WHEN** the maintainer runs the documented packaging process
- **THEN** the system produces a Windows executable artifact that can start the memo application with its required runtime resources
