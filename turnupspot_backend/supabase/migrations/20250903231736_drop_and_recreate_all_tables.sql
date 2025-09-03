-- Drop all existing tables (order matters due to foreign keys)
DROP TABLE IF EXISTS game_players CASCADE;
DROP TABLE IF EXISTS game_teams CASCADE;
DROP TABLE IF EXISTS game_day_participants CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS games CASCADE;
DROP TABLE IF EXISTS team_members CASCADE;
DROP TABLE IF EXISTS teams CASCADE;
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS chat_rooms CASCADE;
DROP TABLE IF EXISTS event_attendees CASCADE;
DROP TABLE IF EXISTS vendor_services CASCADE;
DROP TABLE IF EXISTS vendors CASCADE;
DROP TABLE IF EXISTS sport_group_members CASCADE;
DROP TABLE IF EXISTS playing_days CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS sport_groups CASCADE;
DROP TABLE IF EXISTS sports CASCADE;
DROP TABLE IF EXISTS users CASCADE;


-- Drop existing enum types
DROP TYPE IF EXISTS userrole CASCADE;
DROP TYPE IF EXISTS eventstatus CASCADE;
DROP TYPE IF EXISTS eventtype CASCADE;
DROP TYPE IF EXISTS attendeestatus CASCADE;
DROP TYPE IF EXISTS chatroomtype CASCADE;
DROP TYPE IF EXISTS messagetype CASCADE;
DROP TYPE IF EXISTS sportstype CASCADE;
DROP TYPE IF EXISTS memberrole CASCADE;
DROP TYPE IF EXISTS gamestatus CASCADE;
DROP TYPE IF EXISTS playerstatus CASCADE;
DROP TYPE IF EXISTS matchstatus CASCADE;
DROP TYPE IF EXISTS day CASCADE;
DROP TYPE IF EXISTS player_status CASCADE;

-- Create enum types
CREATE TYPE userrole AS ENUM ('USER', 'VENDOR', 'ADMIN', 'SUPERADMIN');
CREATE TYPE eventstatus AS ENUM ('DRAFT', 'PUBLISHED', 'CANCELLED', 'COMPLETED');
CREATE TYPE eventtype AS ENUM ('CONCERT', 'CONFERENCE', 'WORKSHOP', 'PARTY', 'SPORTS', 'EXHIBITION', 'FESTIVAL', 'OTHER');
CREATE TYPE attendeestatus AS ENUM ('REGISTERED', 'CONFIRMED', 'ATTENDED', 'NO_SHOW', 'CANCELLED');
CREATE TYPE chatroomtype AS ENUM ('SPORT_GROUP', 'EVENT', 'DIRECT');
CREATE TYPE messagetype AS ENUM ('TEXT', 'IMAGE', 'FILE', 'SYSTEM');
CREATE TYPE sportstype AS ENUM ('FOOTBALL', 'BASKETBALL', 'TENNIS', 'VOLLEYBALL', 'CRICKET', 'BASEBALL', 'RUGBY', 'HOCKEY', 'BADMINTON', 'TABLE_TENNIS', 'SWIMMING', 'ATHLETICS', 'OTHER');
CREATE TYPE memberrole AS ENUM ('ADMIN', 'MEMBER');
CREATE TYPE gamestatus AS ENUM ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
CREATE TYPE playerstatus AS ENUM ('EXPECTED', 'ARRIVED', 'DELAYED', 'ABSENT');
CREATE TYPE matchstatus AS ENUM ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
CREATE TYPE day AS ENUM ('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY');



-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    phone_number VARCHAR,
    date_of_birth TIMESTAMP,
    profile_image_url VARCHAR,
    bio TEXT,
    role userrole NOT NULL,
    is_active BOOLEAN NOT NULL,
    is_verified BOOLEAN NOT NULL,
    activation_token VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create sports table
CREATE TABLE sports (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    type VARCHAR NOT NULL,
    max_players_per_team INTEGER,
    min_teams INTEGER,
    players_per_match INTEGER,
    requires_referee BOOLEAN,
    rules JSON,
    created_by INTEGER REFERENCES users(id),
    is_default BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create sport_groups table
CREATE TABLE sport_groups (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    venue_name VARCHAR NOT NULL,
    venue_address VARCHAR NOT NULL,
    venue_image_url VARCHAR,
    venue_latitude DOUBLE PRECISION,
    venue_longitude DOUBLE PRECISION,
    playing_days VARCHAR NOT NULL,
    game_start_time TIMESTAMP NOT NULL,
    game_end_time TIMESTAMP NOT NULL,
    max_teams INTEGER NOT NULL,
    max_players_per_team INTEGER NOT NULL,
    rules VARCHAR,
    referee_required BOOLEAN,
    created_by VARCHAR NOT NULL,
    sports_type sportstype NOT NULL,
    creator_id INTEGER NOT NULL REFERENCES users(id),
    is_active BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (created_by) REFERENCES users(email)
);

-- Create events table
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT NOT NULL,
    event_type eventtype NOT NULL,
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP NOT NULL,
    venue_name VARCHAR NOT NULL,
    venue_address VARCHAR NOT NULL,
    venue_latitude DOUBLE PRECISION,
    venue_longitude DOUBLE PRECISION,
    max_attendees INTEGER,
    ticket_price DOUBLE PRECISION,
    is_free BOOLEAN,
    registration_deadline TIMESTAMP,
    cover_image_url VARCHAR,
    additional_images TEXT,
    status eventstatus,
    creator_id INTEGER NOT NULL REFERENCES users(id),
    is_public BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create vendors table
CREATE TABLE vendors (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
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
    average_rating DOUBLE PRECISION,
    total_reviews INTEGER,
    is_verified BOOLEAN,
    is_active BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create playing_days table
CREATE TABLE playing_days (
    id VARCHAR PRIMARY KEY,
    sport_group_id VARCHAR REFERENCES sport_groups(id) ON DELETE CASCADE,
    day day
);

-- Create sport_group_members table
CREATE TABLE sport_group_members (
    id SERIAL PRIMARY KEY,
    sport_group_id VARCHAR NOT NULL REFERENCES sport_groups(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    role memberrole,
    is_approved BOOLEAN,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create teams table
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    sport_group_id VARCHAR NOT NULL REFERENCES sport_groups(id)
);

-- Create chat_rooms table
CREATE TABLE chat_rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    room_type chatroomtype NOT NULL,
    sport_group_id VARCHAR REFERENCES sport_groups(id),
    event_id INTEGER REFERENCES events(id),
    is_active BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create event_attendees table
CREATE TABLE event_attendees (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    status attendeestatus,
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    check_in_time TIMESTAMP,
    payment_id VARCHAR,
    amount_paid DOUBLE PRECISION
);

-- Create vendor_services table
CREATE TABLE vendor_services (
    id SERIAL PRIMARY KEY,
    vendor_id INTEGER NOT NULL REFERENCES vendors(id),
    name VARCHAR NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR NOT NULL,
    base_price DOUBLE PRECISION,
    price_unit VARCHAR,
    price_range_min DOUBLE PRECISION,
    price_range_max DOUBLE PRECISION,
    duration VARCHAR,
    includes TEXT,
    requirements TEXT,
    is_available BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create games table (fixed reserved keyword issue)
CREATE TABLE games (
    id VARCHAR PRIMARY KEY,
    sport_group_id VARCHAR NOT NULL REFERENCES sport_groups(id),
    game_date TIMESTAMP NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    referee_id INTEGER REFERENCES sport_group_members(id),
    assistant_referee_id INTEGER REFERENCES sport_group_members(id),
    status gamestatus,
    game_time INTEGER,  -- Changed from current_time (reserved keyword)
    is_timer_running BOOLEAN,
    notes TEXT,
    weather_conditions VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    completed_matches JSON,
    current_match JSON,
    upcoming_match JSON,
    coin_toss_state JSON,
    -- Additional columns from ba462233fa5e migration
    match_duration_seconds INTEGER,
    timer_started_at TIMESTAMP,
    timer_remaining_seconds INTEGER,
    timer_is_running BOOLEAN,
    current_match_team_a VARCHAR,
    current_match_team_b VARCHAR,
    current_match_team_a_score INTEGER,
    current_match_team_b_score INTEGER,
    current_match_started_at TIMESTAMP,
    team_rotation_order TEXT,
    current_rotation_index INTEGER
);

-- Create chat_messages table
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    chat_room_id INTEGER NOT NULL REFERENCES chat_rooms(id),
    sender_id INTEGER NOT NULL REFERENCES users(id),
    message_type messagetype,
    content TEXT NOT NULL,
    file_url VARCHAR,
    file_name VARCHAR,
    file_size INTEGER,
    is_edited BOOLEAN,
    edited_at TIMESTAMP,
    is_deleted BOOLEAN,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create team_members table
CREATE TABLE team_members (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES teams(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    arrival_time TIMESTAMP
);

-- Create game_day_participants table
CREATE TABLE game_day_participants (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR NOT NULL REFERENCES games(id),
    name VARCHAR NOT NULL,
    email VARCHAR,
    phone VARCHAR,
    team INTEGER,
    is_registered_user BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create game_teams table
CREATE TABLE game_teams (
    id VARCHAR PRIMARY KEY,
    game_id VARCHAR NOT NULL REFERENCES games(id),
    team_name VARCHAR NOT NULL,
    team_number INTEGER NOT NULL,
    captain_id INTEGER REFERENCES sport_group_members(id),
    score INTEGER,
    goals_scored INTEGER,
    goals_conceded INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create matches table (from f46abf58eb28 migration)
CREATE TABLE matches (
    id VARCHAR PRIMARY KEY,
    game_id VARCHAR NOT NULL REFERENCES games(id),
    team_a_id VARCHAR NOT NULL REFERENCES game_teams(id),
    team_b_id VARCHAR NOT NULL REFERENCES game_teams(id),
    team_a_score INTEGER,
    team_b_score INTEGER,
    winner_id VARCHAR REFERENCES game_teams(id),
    is_draw BOOLEAN,
    status matchstatus,
    referee_id INTEGER REFERENCES sport_group_members(id),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create game_players table
CREATE TABLE game_players (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR NOT NULL REFERENCES games(id),
    team_id VARCHAR REFERENCES game_teams(id),
    member_id INTEGER NOT NULL REFERENCES sport_group_members(id),
    status playerstatus,
    arrival_time TIMESTAMP,
    check_in_location_lat VARCHAR,
    check_in_location_lng VARCHAR,
    goals_scored INTEGER,
    assists INTEGER,
    yellow_cards INTEGER,
    red_cards INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_id ON users(id);
CREATE INDEX ix_sports_id ON sports(id);
CREATE INDEX ix_sport_groups_id ON sport_groups(id);
CREATE INDEX ix_events_id ON events(id);
CREATE INDEX ix_events_title ON events(title);
CREATE INDEX ix_vendors_id ON vendors(id);
CREATE INDEX ix_vendors_business_name ON vendors(business_name);
CREATE INDEX ix_sport_group_members_id ON sport_group_members(id);
CREATE INDEX ix_teams_id ON teams(id);
CREATE INDEX ix_chat_rooms_id ON chat_rooms(id);
CREATE INDEX ix_event_attendees_id ON event_attendees(id);
CREATE INDEX ix_vendor_services_id ON vendor_services(id);
CREATE INDEX ix_games_id ON games(id);
CREATE INDEX ix_chat_messages_id ON chat_messages(id);
CREATE INDEX ix_team_members_id ON team_members(id);
CREATE INDEX ix_game_day_participants_id ON game_day_participants(id);
CREATE INDEX ix_game_teams_id ON game_teams(id);
CREATE INDEX ix_matches_id ON matches(id);
CREATE INDEX ix_game_players_id ON game_players(id);

-- Additional performance indexes
CREATE INDEX idx_matches_game_id ON matches(game_id);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_game_day_participants_game_id ON game_day_participants(game_id);
CREATE INDEX idx_game_day_participants_email ON game_day_participants(email);
CREATE INDEX idx_game_teams_game_id ON game_teams(game_id);
CREATE INDEX idx_game_players_game_id ON game_players(game_id);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_sports_updated_at BEFORE UPDATE ON sports FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_sport_groups_updated_at BEFORE UPDATE ON sport_groups FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_vendors_updated_at BEFORE UPDATE ON vendors FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_chat_rooms_updated_at BEFORE UPDATE ON chat_rooms FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_vendor_services_updated_at BEFORE UPDATE ON vendor_services FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_games_updated_at BEFORE UPDATE ON games FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_chat_messages_updated_at BEFORE UPDATE ON chat_messages FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_matches_updated_at BEFORE UPDATE ON matches FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_game_players_updated_at BEFORE UPDATE ON game_players FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_game_day_participants_updated_at BEFORE UPDATE ON game_day_participants FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

