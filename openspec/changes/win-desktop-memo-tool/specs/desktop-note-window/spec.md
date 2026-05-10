## ADDED Requirements

### Requirement: Floating desktop panel
The system SHALL provide a primary memo window that can remain visible as a floating desktop panel while the application is running.

#### Scenario: Show floating window on launch
- **WHEN** the user launches the application
- **THEN** the system displays the primary memo window in a visible desktop-floating state

#### Scenario: Keep panel accessible during use
- **WHEN** the primary memo window is visible
- **THEN** the system keeps the window usable for viewing and managing memo events without requiring additional navigation

### Requirement: Hide and restore main window
The system SHALL allow the user to hide the primary memo window and restore it later without losing current event data.

#### Scenario: Hide main window
- **WHEN** the user triggers the hide action from the primary memo window
- **THEN** the system removes the window from the visible desktop area and keeps the application running

#### Scenario: Restore hidden main window
- **WHEN** the user triggers the restore action after the main window has been hidden
- **THEN** the system makes the primary memo window visible again with the existing event list and input state preserved
