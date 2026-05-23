## ADDED Requirements

### Requirement: Display animated reminder alert
The system SHALL display a visible animated reminder alert when a memo event becomes due.

#### Scenario: Trigger reminder animation at due time
- **WHEN** a pending event becomes due while the application is running
- **THEN** the system opens a reminder alert with animation and displays the event information

### Requirement: Dismiss active reminder
The system SHALL allow the user to close an active reminder so that the reminder is no longer shown for the current due occurrence.

#### Scenario: Close reminder alert
- **WHEN** the user selects the close action on an active reminder alert
- **THEN** the system hides the alert and records that the current reminder occurrence has been dismissed

### Requirement: Snooze active reminder
The system SHALL allow the user to postpone an active reminder to a later time.

#### Scenario: Snooze reminder with preset duration
- **WHEN** the user selects a snooze option for an active reminder
- **THEN** the system updates the reminder to trigger again at the postponed time and closes the current alert
