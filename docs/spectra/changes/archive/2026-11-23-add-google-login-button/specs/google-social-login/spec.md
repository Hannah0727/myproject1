## Purpose

The google-social-login capability lets visitors start the configured Google OAuth flow from the application login page. It exposes the already configured django-allauth Google provider without replacing password login.

## ADDED Requirements

### Requirement: Google login entry is available on the login page

The system SHALL display a Google login action on the account login page for unauthenticated visitors. The action SHALL use django-allauth's configured Google provider login URL and SHALL include text that identifies it as Google login.

#### Scenario: Visitor starts Google login

- **WHEN** an unauthenticated visitor opens the account login page and activates the Google login action
- **THEN** the browser requests the login URL generated for the Google socialaccount provider

### Requirement: Password login remains available

The system SHALL preserve the existing account login form and account sign-up navigation while adding the Google login action.

#### Scenario: Visitor sees both authentication paths

- **WHEN** an unauthenticated visitor opens the account login page
- **THEN** the page contains the existing password login form, the Google login action, and the account sign-up link
