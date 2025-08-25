# Requirements Document

## Introduction

The team formation system in TurnUpSpot has several critical issues preventing proper game functionality. When users click "Play Ball" after drafting teams, the game shows no available teams because the GameTeam records are not being properly created and populated in the database. This prevents the live match functionality from working correctly.

## Requirements

### Requirement 1

**User Story:** As a sport group admin, I want teams to be automatically created in the database when captains are assigned, so that the game can track team information properly.

#### Acceptance Criteria

1. WHEN a captain is assigned to a team THEN the system SHALL create a GameTeam record if it doesn't exist
2. WHEN a GameTeam is created THEN it SHALL have the correct game_id, team_name, team_number, and captain_id
3. WHEN teams are created THEN they SHALL be immediately available via the /available-teams API endpoint

### Requirement 2

**User Story:** As a sport group member, I want to be able to assign captains without requiring exactly 10 players, so that smaller groups can still form teams and play games.

#### Acceptance Criteria

1. WHEN there are at least 2 checked-in players THEN captain assignment SHALL be allowed
2. WHEN captain assignment occurs THEN it SHALL work for any number of players >= 2
3. WHEN fewer than 10 players are present THEN the system SHALL still allow team formation

### Requirement 3

**User Story:** As a developer, I want the GamePlayer model to properly track captain status, so that the system can identify team captains correctly.

#### Acceptance Criteria

1. WHEN the GamePlayer model is defined THEN it SHALL include an is_captain boolean field
2. WHEN a player is assigned as captain THEN their is_captain field SHALL be set to True
3. WHEN captain status is queried THEN it SHALL return accurate information from the database

### Requirement 4

**User Story:** As a sport group member, I want teams to be properly populated when players are drafted, so that the live match system can access team information.

#### Acceptance Criteria

1. WHEN players are selected for teams THEN their team_id SHALL be properly set in the GamePlayer table
2. WHEN team selection is complete THEN the GameTeam records SHALL contain accurate player counts
3. WHEN the game state is queried THEN it SHALL return populated teams with correct player assignments

### Requirement 5

**User Story:** As a sport group member, I want the /available-teams endpoint to return accurate team information, so that the live match interface can display and use teams correctly.

#### Acceptance Criteria

1. WHEN teams exist in the database THEN the /available-teams endpoint SHALL return them
2. WHEN no teams have played yet THEN all teams SHALL be marked as available
3. WHEN teams are returned THEN they SHALL include id, name, team_number, and captain_id information

### Requirement 6

**User Story:** As a sport group member, I want the game state endpoint to return complete team and player information, so that the live match interface can function properly.

#### Acceptance Criteria

1. WHEN the /game/{id}/state endpoint is called THEN it SHALL return populated teams array
2. WHEN the /game/{id} endpoint is called THEN it SHALL return teams with complete information
3. WHEN team information is requested THEN it SHALL include all associated players and their status
