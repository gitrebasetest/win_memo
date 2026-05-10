## ADDED Requirements

### Requirement: Resolve workday reminders using holiday data
The system SHALL use holiday and make-up workday data to determine whether a calendar date is a valid workday for workday-based reminders.

#### Scenario: Skip statutory holiday for workday reminder
- **WHEN** a configured workday reminder would otherwise fall on a date marked as a holiday in the holiday dataset
- **THEN** the system schedules the reminder for the next valid workday instead of triggering on the holiday

#### Scenario: Accept make-up workday on weekend
- **WHEN** a configured workday reminder falls on a weekend date marked as a make-up workday in the holiday dataset
- **THEN** the system treats that date as a valid workday for reminder scheduling

### Requirement: Refresh holiday data from network
The system SHALL be able to retrieve holiday data from a network source and cache it locally for later scheduling decisions.

#### Scenario: Cache fetched holiday data
- **WHEN** the application successfully retrieves holiday data from the configured network source
- **THEN** the system stores the retrieved date classifications locally for subsequent scheduling use

#### Scenario: Use cached holiday data when offline
- **WHEN** the application cannot reach the configured holiday data source but cached data for the required dates exists
- **THEN** the system continues workday reminder scheduling using the cached holiday data
