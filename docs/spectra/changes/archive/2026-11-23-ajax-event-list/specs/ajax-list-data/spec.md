## Purpose

The ajax-list-data capability defines a reusable contract for displaying persisted-record collections through asynchronous requests. It bounds data transfer with pagination and makes loading, empty, and failed requests observable to users.

## ADDED Requirements

### Requirement: Asynchronous persisted-record lists

The system SHALL render the page shell for a persisted-record list and SHALL obtain the list records from a same-origin asynchronous endpoint. The endpoint SHALL return the item data required by the list and pagination metadata. Static lists and one-off form option lists are outside this requirement.

#### Scenario: Visitor opens an event list

- **WHEN** a visitor opens the event list page
- **THEN** the browser requests the event records from the asynchronous endpoint
- **AND** renders returned records without a full page reload

### Requirement: Bounded list pagination

The asynchronous endpoint SHALL accept `page` and active filter parameters and SHALL return the current page, total page count, total item count, and adjacent-page availability. The list UI SHALL preserve active filters when requesting a new page and SHALL expose previous and next page controls.

#### Scenario: Visitor moves through filtered results

- **WHEN** a visitor with an active search filter selects the next page
- **THEN** the request includes the active filter and selected page
- **AND** the UI renders the returned records and adjacent-page availability

##### Example: Search result page

- **GIVEN** `q=羽球` and `page=2`
- **WHEN** the endpoint processes the request
- **THEN** the response identifies page 2 and includes `q=羽球`

### Requirement: Observable list request states

The list UI SHALL distinguish loading, successful empty results, and failed requests. While a request is pending, the UI SHALL prevent duplicate pagination requests. A failed initial request SHALL show an error and retry action. If a later request fails after records have been rendered, the UI SHALL retain those records and show an error with a retry action.

#### Scenario: Initial request fails

- **WHEN** the first asynchronous list request fails
- **THEN** the UI displays an error state and retry action
- **AND** it does not display the failure as an empty result

#### Scenario: Later page request fails

- **GIVEN** the UI has rendered records from a successful request
- **WHEN** a request for another page fails
- **THEN** the existing records remain visible
- **AND** the UI displays an error and retry action
