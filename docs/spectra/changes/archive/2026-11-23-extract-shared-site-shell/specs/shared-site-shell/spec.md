## Purpose

The shared site shell provides one Django template layout and one navigation experience for the Jiumingah website. It prevents repeated document scaffolding while preserving each page's existing application behavior.

## ADDED Requirements

### Requirement: Reusable site layout

The system SHALL provide a core-owned Django base template that supplies the document structure, one Tailwind CDN stylesheet script, one core-owned shared stylesheet link, a default brand title, and overridable title and content blocks. Pages that adopt the base template SHALL render their own primary content through the content block without adding a second document structure or duplicate shared resource load.

#### Scenario: An activity page adopts the shared layout

- **WHEN** a visitor opens an activity list, detail, or creation page
- **THEN** the response renders the shared document structure and navbar once while preserving that page's existing primary activity content

#### Scenario: An account page adopts the shared layout

- **WHEN** a visitor opens the login, signup, or logout page
- **THEN** the response renders the shared document structure and navbar once while preserving that page's existing account form or confirmation content

### Requirement: Shared navigation links

The system SHALL render a core-owned navbar before page content with a brand link to the named home route and an activity-discovery link to the named activity-list route. The navbar SHALL link to the home-page `how` and `categories` sections using the named home route followed by the corresponding fragment, so the links resolve from every adopting page.

#### Scenario: Visitor follows a home section link from an activity page

- **WHEN** a visitor selects the navbar link for the how-it-works section while viewing an activity page
- **THEN** the browser receives a link targeting the home route with the `#how` fragment

#### Scenario: Visitor follows the brand link

- **WHEN** a visitor selects the navbar brand from an account page
- **THEN** the browser receives a link targeting the named home route

### Requirement: Authentication-aware navigation actions

The system SHALL render navigation account actions from Django's existing authentication context. For an anonymous visitor, the navbar SHALL provide login and signup links. For an authenticated visitor, the navbar SHALL provide a link to the named activity-creation route and a POST logout form that includes a CSRF token.

#### Scenario: Anonymous visitor views a shared-layout page

- **WHEN** an anonymous visitor opens a page that adopts the shared layout
- **THEN** the navbar displays login and signup actions and does not display the logout form

#### Scenario: Authenticated visitor views a shared-layout page

- **WHEN** an authenticated visitor opens a page that adopts the shared layout
- **THEN** the navbar displays the activity-creation action and a CSRF-protected POST logout form
