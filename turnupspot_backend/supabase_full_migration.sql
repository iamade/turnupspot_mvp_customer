BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> f48844ffe2e7

CREATE TYPE userrole AS ENUM ('USER', 'VENDOR', 'ADMIN', 'SUPERADMIN');

CREATE TABLE users (
    id SERIAL NOT NULL, 
    email VARCHAR NOT NULL, 
    hashed_password VARCHAR NOT NULL, 
    first_name VARCHAR NOT NULL, 
    last_name VARCHAR NOT NULL, 
    phone_number VARCHAR, 
    date_of_birth TIMESTAMP WITHOUT TIME ZONE, 
    profile_image_url VARCHAR, 
    bio TEXT, 
    role userrole NOT NULL, 
    is_active BOOLEAN NOT NULL, 
    is_verified BOOLEAN NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE INDEX ix_users_id ON users (id);

CREATE TYPE eventtype AS ENUM ('CONCERT', 'CONFERENCE', 'WORKSHOP', 'PARTY', 'SPORTS', 'EXHIBITION', 'FESTIVAL', 'OTHER');

CREATE TYPE eventstatus AS ENUM ('DRAFT', 'PUBLISHED', 'CANCELLED', 'COMPLETED');

CREATE TABLE events (
    id SERIAL NOT NULL, 
    title VARCHAR NOT NULL, 
    description TEXT NOT NULL, 
    event_type eventtype NOT NULL, 
    start_datetime TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    end_datetime TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    venue_name VARCHAR NOT NULL, 
    venue_address VARCHAR NOT NULL, 
    venue_latitude FLOAT, 
    venue_longitude FLOAT, 
    max_attendees INTEGER, 
    ticket_price FLOAT, 
    is_free BOOLEAN, 
    registration_deadline TIMESTAMP WITHOUT TIME ZONE, 
    cover_image_url VARCHAR, 
    additional_images TEXT, 
    status eventstatus, 
    creator_id INTEGER NOT NULL, 
    is_public BOOLEAN, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(creator_id) REFERENCES users (id)
);

CREATE INDEX ix_events_id ON events (id);

CREATE INDEX ix_events_title ON events (title);

CREATE TYPE sportstype AS ENUM ('FOOTBALL', 'BASKETBALL', 'TENNIS', 'VOLLEYBALL', 'CRICKET', 'BASEBALL', 'RUGBY', 'HOCKEY', 'BADMINTON', 'TABLE_TENNIS', 'SWIMMING', 'ATHLETICS', 'OTHER');

CREATE TABLE sport_groups (
    id VARCHAR NOT NULL, 
    name VARCHAR NOT NULL, 
    description VARCHAR, 
    venue_name VARCHAR NOT NULL, 
    venue_address VARCHAR NOT NULL, 
    venue_image_url VARCHAR, 
    venue_latitude FLOAT, 
    venue_longitude FLOAT, 
    playing_days VARCHAR NOT NULL, 
    game_start_time TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    game_end_time TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    max_teams INTEGER NOT NULL, 
    max_players_per_team INTEGER NOT NULL, 
    rules VARCHAR, 
    referee_required BOOLEAN, 
    created_by VARCHAR NOT NULL, 
    sports_type sportstype NOT NULL, 
    creator_id INTEGER NOT NULL, 
    is_active BOOLEAN, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(created_by) REFERENCES users (email), 
    FOREIGN KEY(creator_id) REFERENCES users (id)
);

CREATE INDEX ix_sport_groups_id ON sport_groups (id);

CREATE TABLE sports (
    id SERIAL NOT NULL, 
    name VARCHAR NOT NULL, 
    type VARCHAR NOT NULL, 
    max_players_per_team INTEGER, 
    min_teams INTEGER, 
    players_per_match INTEGER, 
    requires_referee BOOLEAN, 
    rules JSON, 
    created_by INTEGER, 
    is_default BOOLEAN, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(created_by) REFERENCES users (id), 
    UNIQUE (name)
);

CREATE INDEX ix_sports_id ON sports (id);

CREATE TABLE vendors (
    id SERIAL NOT NULL, 
    user_id INTEGER NOT NULL, 
    business_name VARCHAR NOT NULL, 
    business_type VARCHAR NOT NULL, 
    description TEXT NOT NULL, 
    business_phone VARCHAR, 
    business_email VARCHAR, 
    website_url VARCHAR, 
    business_address VARCHAR, 
    service_areas TEXT, 
    years_in_business INTEGER, 
    license_number VARCHAR, 
    insurance_verified BOOLEAN, 
    logo_url VARCHAR, 
    portfolio_images TEXT, 
    average_rating FLOAT, 
    total_reviews INTEGER, 
    is_verified BOOLEAN, 
    is_active BOOLEAN, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_vendors_business_name ON vendors (business_name);

CREATE INDEX ix_vendors_id ON vendors (id);

CREATE TYPE chatroomtype AS ENUM ('SPORT_GROUP', 'EVENT', 'DIRECT');

CREATE TABLE chat_rooms (
    id SERIAL NOT NULL, 
    name VARCHAR, 
    room_type chatroomtype NOT NULL, 
    sport_group_id VARCHAR, 
    event_id INTEGER, 
    is_active BOOLEAN, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(event_id) REFERENCES events (id), 
    FOREIGN KEY(sport_group_id) REFERENCES sport_groups (id)
);

CREATE INDEX ix_chat_rooms_id ON chat_rooms (id);

CREATE TYPE attendeestatus AS ENUM ('REGISTERED', 'CONFIRMED', 'ATTENDED', 'NO_SHOW', 'CANCELLED');

CREATE TABLE event_attendees (
    id SERIAL NOT NULL, 
    event_id INTEGER NOT NULL, 
    user_id INTEGER NOT NULL, 
    status attendeestatus, 
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    check_in_time TIMESTAMP WITHOUT TIME ZONE, 
    payment_id VARCHAR, 
    amount_paid FLOAT, 
    PRIMARY KEY (id), 
    FOREIGN KEY(event_id) REFERENCES events (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_event_attendees_id ON event_attendees (id);

CREATE TYPE memberrole AS ENUM ('ADMIN', 'MEMBER');

CREATE TABLE sport_group_members (
    id SERIAL NOT NULL, 
    sport_group_id VARCHAR NOT NULL, 
    user_id INTEGER NOT NULL, 
    role memberrole, 
    is_approved BOOLEAN, 
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(sport_group_id) REFERENCES sport_groups (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_sport_group_members_id ON sport_group_members (id);

CREATE TABLE teams (
    id SERIAL NOT NULL, 
    name VARCHAR NOT NULL, 
    sport_group_id VARCHAR NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(sport_group_id) REFERENCES sport_groups (id)
);

CREATE INDEX ix_teams_id ON teams (id);

CREATE TABLE vendor_services (
    id SERIAL NOT NULL, 
    vendor_id INTEGER NOT NULL, 
    name VARCHAR NOT NULL, 
    description TEXT NOT NULL, 
    category VARCHAR NOT NULL, 
    base_price FLOAT, 
    price_unit VARCHAR, 
    price_range_min FLOAT, 
    price_range_max FLOAT, 
    duration VARCHAR, 
    includes TEXT, 
    requirements TEXT, 
    is_available BOOLEAN, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(vendor_id) REFERENCES vendors (id)
);

CREATE INDEX ix_vendor_services_id ON vendor_services (id);

CREATE TYPE messagetype AS ENUM ('TEXT', 'IMAGE', 'FILE', 'SYSTEM');

CREATE TABLE chat_messages (
    id SERIAL NOT NULL, 
    chat_room_id INTEGER NOT NULL, 
    sender_id INTEGER NOT NULL, 
    message_type messagetype, 
    content TEXT NOT NULL, 
    file_url VARCHAR, 
    file_name VARCHAR, 
    file_size INTEGER, 
    is_edited BOOLEAN, 
    edited_at TIMESTAMP WITHOUT TIME ZONE, 
    is_deleted BOOLEAN, 
    deleted_at TIMESTAMP WITHOUT TIME ZONE, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(chat_room_id) REFERENCES chat_rooms (id), 
    FOREIGN KEY(sender_id) REFERENCES users (id)
);

CREATE INDEX ix_chat_messages_id ON chat_messages (id);

CREATE TYPE gamestatus AS ENUM ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');

CREATE TABLE games (
    id SERIAL NOT NULL, 
    sport_group_id VARCHAR NOT NULL, 
    game_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    start_time TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    end_time TIMESTAMP WITHOUT TIME ZONE, 
    referee_id INTEGER, 
    assistant_referee_id INTEGER, 
    status gamestatus, 
    "current_time" INTEGER, 
    is_timer_running BOOLEAN, 
    notes TEXT, 
    weather_conditions VARCHAR, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(assistant_referee_id) REFERENCES sport_group_members (id), 
    FOREIGN KEY(referee_id) REFERENCES sport_group_members (id), 
    FOREIGN KEY(sport_group_id) REFERENCES sport_groups (id)
);

CREATE INDEX ix_games_id ON games (id);

CREATE TABLE team_members (
    id SERIAL NOT NULL, 
    team_id INTEGER NOT NULL, 
    user_id INTEGER NOT NULL, 
    arrival_time TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(team_id) REFERENCES teams (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_team_members_id ON team_members (id);

CREATE TABLE game_teams (
    id SERIAL NOT NULL, 
    game_id INTEGER NOT NULL, 
    team_name VARCHAR NOT NULL, 
    team_number INTEGER NOT NULL, 
    captain_id INTEGER, 
    score INTEGER, 
    goals_scored INTEGER, 
    goals_conceded INTEGER, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(captain_id) REFERENCES sport_group_members (id), 
    FOREIGN KEY(game_id) REFERENCES games (id)
);

CREATE INDEX ix_game_teams_id ON game_teams (id);

CREATE TYPE playerstatus AS ENUM ('EXPECTED', 'ARRIVED', 'DELAYED', 'ABSENT');

CREATE TABLE game_players (
    id SERIAL NOT NULL, 
    game_id INTEGER NOT NULL, 
    team_id INTEGER, 
    member_id INTEGER NOT NULL, 
    status playerstatus, 
    arrival_time TIMESTAMP WITHOUT TIME ZONE, 
    check_in_location_lat VARCHAR, 
    check_in_location_lng VARCHAR, 
    goals_scored INTEGER, 
    assists INTEGER, 
    yellow_cards INTEGER, 
    red_cards INTEGER, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(game_id) REFERENCES games (id), 
    FOREIGN KEY(member_id) REFERENCES sport_group_members (id), 
    FOREIGN KEY(team_id) REFERENCES game_teams (id)
);

CREATE INDEX ix_game_players_id ON game_players (id);

INSERT INTO alembic_version (version_num) VALUES ('f48844ffe2e7') RETURNING alembic_version.version_num;

-- Running upgrade f48844ffe2e7 -> 123456789abc

ALTER TABLE users ADD COLUMN activation_token VARCHAR;

UPDATE alembic_version SET version_num='123456789abc' WHERE alembic_version.version_num = 'f48844ffe2e7';

COMMIT;

