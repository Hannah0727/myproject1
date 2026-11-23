## ADDED Requirements

### Requirement: Asynchronous event-list data is cached and invalidated after event creation

The system SHALL cache successful event-list asynchronous endpoint responses using the normalized search query, resolved page, and current event-list cache version. The system SHALL retain the existing JSON response structure and configured cache lifetime. After a new event is created and its database transaction commits, the system SHALL advance the event-list cache version so every later event-list request bypasses responses cached before that creation, regardless of search query or page. Cache service failures MUST NOT prevent the endpoint from returning a freshly generated successful response.

#### Scenario: A repeated request reuses an event-list response

- **WHEN** a visitor requests the event-list asynchronous endpoint twice with the same normalized search query and resolved page before the cache expires or the cache version changes
- **THEN** the second response SHALL reuse the cached successful response and preserve the existing JSON structure

#### Scenario: A new event invalidates every cached list variant

- **WHEN** a new event is created through any ORM entry point and its database transaction commits
- **THEN** the next event-list asynchronous request for any search query or page SHALL not use a response cached before that event was created

#### Scenario: A creation transaction is rolled back

- **WHEN** creation of a new event is rolled back before the database transaction commits
- **THEN** the event-list cache version SHALL remain unchanged

#### Scenario: The cache service is unavailable

- **WHEN** the event-list asynchronous endpoint cannot read or write its cache
- **THEN** the endpoint SHALL generate and return a successful response using its existing list-query behavior
