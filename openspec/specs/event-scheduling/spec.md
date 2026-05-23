## ADDED Requirements

### Requirement: Manage timed memo events
The system SHALL allow the user to create, edit, delete, and list memo events that include event content and a supported reminder rule.

#### Scenario: Create one-time event with absolute datetime
- **WHEN** the user enters event information and a valid absolute date and time and saves the event
- **THEN** the system stores the event and shows it in the event list

#### Scenario: Create recurring weekly event
- **WHEN** the user selects a weekly reminder rule such as Saturday at 15:00 and saves the event
- **THEN** the system stores the weekly schedule rule and shows the event in the event list

#### Scenario: Create recurring workday event
- **WHEN** the user selects a workday reminder rule such as every workday at 17:00 and saves the event
- **THEN** the system stores the workday schedule rule and shows the event in the event list

#### Scenario: Edit existing event
- **WHEN** the user updates the content or reminder rule of an existing event and saves the changes
- **THEN** the system persists the updated event values and reflects them in the event list

#### Scenario: Delete existing event
- **WHEN** the user deletes an existing event
- **THEN** the system removes the event from persisted storage and from the event list

### Requirement: Order and track pending reminders
The system SHALL track pending memo events by their active next reminder time so that due events can be identified for reminder display.

#### Scenario: View upcoming events in order
- **WHEN** multiple pending events exist with different next reminder times
- **THEN** the system presents them in time-aware order so the nearest due events are easier to identify

#### Scenario: Mark one-time event as due
- **WHEN** the current local time reaches or passes a one-time event's active reminder time
- **THEN** the system marks the event as due for reminder display

#### Scenario: Advance weekly recurring event after trigger
- **WHEN** a weekly recurring event has been triggered for its current scheduled occurrence
- **THEN** the system computes and stores the next valid weekly reminder time

#### Scenario: Advance workday recurring event after trigger
- **WHEN** a workday recurring event has been triggered for its current scheduled occurrence
- **THEN** the system computes and stores the next valid workday reminder time
