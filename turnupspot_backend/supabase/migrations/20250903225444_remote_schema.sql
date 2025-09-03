

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";






CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";






CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";






CREATE TYPE "public"."attendeestatus" AS ENUM (
    'REGISTERED',
    'CONFIRMED',
    'ATTENDED',
    'NO_SHOW',
    'CANCELLED'
);


ALTER TYPE "public"."attendeestatus" OWNER TO "postgres";


CREATE TYPE "public"."chatroomtype" AS ENUM (
    'SPORT_GROUP',
    'EVENT',
    'DIRECT'
);


ALTER TYPE "public"."chatroomtype" OWNER TO "postgres";


CREATE TYPE "public"."eventstatus" AS ENUM (
    'DRAFT',
    'PUBLISHED',
    'CANCELLED',
    'COMPLETED'
);


ALTER TYPE "public"."eventstatus" OWNER TO "postgres";


CREATE TYPE "public"."eventtype" AS ENUM (
    'CONCERT',
    'CONFERENCE',
    'WORKSHOP',
    'PARTY',
    'SPORTS',
    'EXHIBITION',
    'FESTIVAL',
    'OTHER'
);


ALTER TYPE "public"."eventtype" OWNER TO "postgres";


CREATE TYPE "public"."gamestatus" AS ENUM (
    'SCHEDULED',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED'
);


ALTER TYPE "public"."gamestatus" OWNER TO "postgres";


CREATE TYPE "public"."memberrole" AS ENUM (
    'ADMIN',
    'MEMBER'
);


ALTER TYPE "public"."memberrole" OWNER TO "postgres";


CREATE TYPE "public"."messagetype" AS ENUM (
    'TEXT',
    'IMAGE',
    'FILE',
    'SYSTEM'
);


ALTER TYPE "public"."messagetype" OWNER TO "postgres";


CREATE TYPE "public"."playerstatus" AS ENUM (
    'EXPECTED',
    'ARRIVED',
    'DELAYED',
    'ABSENT'
);


ALTER TYPE "public"."playerstatus" OWNER TO "postgres";


CREATE TYPE "public"."sportstype" AS ENUM (
    'FOOTBALL',
    'BASKETBALL',
    'TENNIS',
    'VOLLEYBALL',
    'CRICKET',
    'BASEBALL',
    'RUGBY',
    'HOCKEY',
    'BADMINTON',
    'TABLE_TENNIS',
    'SWIMMING',
    'ATHLETICS',
    'OTHER'
);


ALTER TYPE "public"."sportstype" OWNER TO "postgres";


CREATE TYPE "public"."userrole" AS ENUM (
    'USER',
    'VENDOR',
    'ADMIN',
    'SUPERADMIN'
);


ALTER TYPE "public"."userrole" OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."alembic_version" (
    "version_num" character varying(32) NOT NULL
);


ALTER TABLE "public"."alembic_version" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."chat_messages" (
    "id" integer NOT NULL,
    "chat_room_id" integer NOT NULL,
    "sender_id" integer NOT NULL,
    "message_type" "public"."messagetype",
    "content" "text" NOT NULL,
    "file_url" character varying,
    "file_name" character varying,
    "file_size" integer,
    "is_edited" boolean,
    "edited_at" timestamp without time zone,
    "is_deleted" boolean,
    "deleted_at" timestamp without time zone,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."chat_messages" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."chat_messages_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."chat_messages_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."chat_messages_id_seq" OWNED BY "public"."chat_messages"."id";



CREATE TABLE IF NOT EXISTS "public"."chat_rooms" (
    "id" integer NOT NULL,
    "name" character varying,
    "room_type" "public"."chatroomtype" NOT NULL,
    "sport_group_id" character varying,
    "event_id" integer,
    "is_active" boolean,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."chat_rooms" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."chat_rooms_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."chat_rooms_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."chat_rooms_id_seq" OWNED BY "public"."chat_rooms"."id";



CREATE TABLE IF NOT EXISTS "public"."event_attendees" (
    "id" integer NOT NULL,
    "event_id" integer NOT NULL,
    "user_id" integer NOT NULL,
    "status" "public"."attendeestatus",
    "registration_date" timestamp with time zone DEFAULT "now"(),
    "check_in_time" timestamp without time zone,
    "payment_id" character varying,
    "amount_paid" double precision
);


ALTER TABLE "public"."event_attendees" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."event_attendees_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."event_attendees_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."event_attendees_id_seq" OWNED BY "public"."event_attendees"."id";



CREATE TABLE IF NOT EXISTS "public"."events" (
    "id" integer NOT NULL,
    "title" character varying NOT NULL,
    "description" "text" NOT NULL,
    "event_type" "public"."eventtype" NOT NULL,
    "start_datetime" timestamp without time zone NOT NULL,
    "end_datetime" timestamp without time zone NOT NULL,
    "venue_name" character varying NOT NULL,
    "venue_address" character varying NOT NULL,
    "venue_latitude" double precision,
    "venue_longitude" double precision,
    "max_attendees" integer,
    "ticket_price" double precision,
    "is_free" boolean,
    "registration_deadline" timestamp without time zone,
    "cover_image_url" character varying,
    "additional_images" "text",
    "status" "public"."eventstatus",
    "creator_id" integer NOT NULL,
    "is_public" boolean,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."events" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."events_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."events_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."events_id_seq" OWNED BY "public"."events"."id";



CREATE TABLE IF NOT EXISTS "public"."game_players" (
    "id" integer NOT NULL,
    "game_id" integer NOT NULL,
    "team_id" integer,
    "member_id" integer NOT NULL,
    "status" "public"."playerstatus",
    "arrival_time" timestamp without time zone,
    "check_in_location_lat" character varying,
    "check_in_location_lng" character varying,
    "goals_scored" integer,
    "assists" integer,
    "yellow_cards" integer,
    "red_cards" integer,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."game_players" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."game_players_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."game_players_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."game_players_id_seq" OWNED BY "public"."game_players"."id";



CREATE TABLE IF NOT EXISTS "public"."game_teams" (
    "id" integer NOT NULL,
    "game_id" integer NOT NULL,
    "team_name" character varying NOT NULL,
    "team_number" integer NOT NULL,
    "captain_id" integer,
    "score" integer,
    "goals_scored" integer,
    "goals_conceded" integer,
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."game_teams" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."game_teams_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."game_teams_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."game_teams_id_seq" OWNED BY "public"."game_teams"."id";



CREATE TABLE IF NOT EXISTS "public"."games" (
    "id" integer NOT NULL,
    "sport_group_id" character varying NOT NULL,
    "game_date" timestamp without time zone NOT NULL,
    "start_time" timestamp without time zone NOT NULL,
    "end_time" timestamp without time zone,
    "referee_id" integer,
    "assistant_referee_id" integer,
    "status" "public"."gamestatus",
    "current_time" integer,
    "is_timer_running" boolean,
    "notes" "text",
    "weather_conditions" character varying,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."games" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."games_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."games_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."games_id_seq" OWNED BY "public"."games"."id";



CREATE TABLE IF NOT EXISTS "public"."sport_group_members" (
    "id" integer NOT NULL,
    "sport_group_id" character varying NOT NULL,
    "user_id" integer NOT NULL,
    "role" "public"."memberrole",
    "is_approved" boolean,
    "joined_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."sport_group_members" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."sport_group_members_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."sport_group_members_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."sport_group_members_id_seq" OWNED BY "public"."sport_group_members"."id";



CREATE TABLE IF NOT EXISTS "public"."sport_groups" (
    "id" character varying NOT NULL,
    "name" character varying NOT NULL,
    "description" character varying,
    "venue_name" character varying NOT NULL,
    "venue_address" character varying NOT NULL,
    "venue_image_url" character varying,
    "venue_latitude" double precision,
    "venue_longitude" double precision,
    "playing_days" character varying NOT NULL,
    "game_start_time" timestamp without time zone NOT NULL,
    "game_end_time" timestamp without time zone NOT NULL,
    "max_teams" integer NOT NULL,
    "max_players_per_team" integer NOT NULL,
    "rules" character varying,
    "referee_required" boolean,
    "created_by" character varying NOT NULL,
    "sports_type" "public"."sportstype" NOT NULL,
    "creator_id" integer NOT NULL,
    "is_active" boolean,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."sport_groups" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."sports" (
    "id" integer NOT NULL,
    "name" character varying NOT NULL,
    "type" character varying NOT NULL,
    "max_players_per_team" integer,
    "min_teams" integer,
    "players_per_match" integer,
    "requires_referee" boolean,
    "rules" json,
    "created_by" integer,
    "is_default" boolean,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."sports" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."sports_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."sports_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."sports_id_seq" OWNED BY "public"."sports"."id";



CREATE TABLE IF NOT EXISTS "public"."team_members" (
    "id" integer NOT NULL,
    "team_id" integer NOT NULL,
    "user_id" integer NOT NULL,
    "arrival_time" timestamp without time zone
);


ALTER TABLE "public"."team_members" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."team_members_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."team_members_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."team_members_id_seq" OWNED BY "public"."team_members"."id";



CREATE TABLE IF NOT EXISTS "public"."teams" (
    "id" integer NOT NULL,
    "name" character varying NOT NULL,
    "sport_group_id" character varying NOT NULL
);


ALTER TABLE "public"."teams" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."teams_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."teams_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."teams_id_seq" OWNED BY "public"."teams"."id";



CREATE TABLE IF NOT EXISTS "public"."users" (
    "id" integer NOT NULL,
    "email" character varying NOT NULL,
    "hashed_password" character varying NOT NULL,
    "first_name" character varying NOT NULL,
    "last_name" character varying NOT NULL,
    "phone_number" character varying,
    "date_of_birth" timestamp without time zone,
    "profile_image_url" character varying,
    "bio" "text",
    "role" "public"."userrole" NOT NULL,
    "is_active" boolean NOT NULL,
    "is_verified" boolean NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone,
    "activation_token" character varying
);


ALTER TABLE "public"."users" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."users_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."users_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."users_id_seq" OWNED BY "public"."users"."id";



CREATE TABLE IF NOT EXISTS "public"."vendor_services" (
    "id" integer NOT NULL,
    "vendor_id" integer NOT NULL,
    "name" character varying NOT NULL,
    "description" "text" NOT NULL,
    "category" character varying NOT NULL,
    "base_price" double precision,
    "price_unit" character varying,
    "price_range_min" double precision,
    "price_range_max" double precision,
    "duration" character varying,
    "includes" "text",
    "requirements" "text",
    "is_available" boolean,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."vendor_services" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."vendor_services_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."vendor_services_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."vendor_services_id_seq" OWNED BY "public"."vendor_services"."id";



CREATE TABLE IF NOT EXISTS "public"."vendors" (
    "id" integer NOT NULL,
    "user_id" integer NOT NULL,
    "business_name" character varying NOT NULL,
    "business_type" character varying NOT NULL,
    "description" "text" NOT NULL,
    "business_phone" character varying,
    "business_email" character varying,
    "website_url" character varying,
    "business_address" character varying,
    "service_areas" "text",
    "years_in_business" integer,
    "license_number" character varying,
    "insurance_verified" boolean,
    "logo_url" character varying,
    "portfolio_images" "text",
    "average_rating" double precision,
    "total_reviews" integer,
    "is_verified" boolean,
    "is_active" boolean,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone
);


ALTER TABLE "public"."vendors" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."vendors_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."vendors_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."vendors_id_seq" OWNED BY "public"."vendors"."id";



ALTER TABLE ONLY "public"."chat_messages" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."chat_messages_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."chat_rooms" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."chat_rooms_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."event_attendees" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."event_attendees_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."events" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."events_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."game_players" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."game_players_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."game_teams" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."game_teams_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."games" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."games_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."sport_group_members" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."sport_group_members_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."sports" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."sports_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."team_members" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."team_members_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."teams" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."teams_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."users" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."users_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."vendor_services" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."vendor_services_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."vendors" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."vendors_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."alembic_version"
    ADD CONSTRAINT "alembic_version_pkc" PRIMARY KEY ("version_num");



ALTER TABLE ONLY "public"."chat_messages"
    ADD CONSTRAINT "chat_messages_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."chat_rooms"
    ADD CONSTRAINT "chat_rooms_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."event_attendees"
    ADD CONSTRAINT "event_attendees_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."events"
    ADD CONSTRAINT "events_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."game_players"
    ADD CONSTRAINT "game_players_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."game_teams"
    ADD CONSTRAINT "game_teams_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."games"
    ADD CONSTRAINT "games_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."sport_group_members"
    ADD CONSTRAINT "sport_group_members_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."sport_groups"
    ADD CONSTRAINT "sport_groups_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."sports"
    ADD CONSTRAINT "sports_name_key" UNIQUE ("name");



ALTER TABLE ONLY "public"."sports"
    ADD CONSTRAINT "sports_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."team_members"
    ADD CONSTRAINT "team_members_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."teams"
    ADD CONSTRAINT "teams_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."vendor_services"
    ADD CONSTRAINT "vendor_services_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."vendors"
    ADD CONSTRAINT "vendors_pkey" PRIMARY KEY ("id");



CREATE INDEX "ix_chat_messages_id" ON "public"."chat_messages" USING "btree" ("id");



CREATE INDEX "ix_chat_rooms_id" ON "public"."chat_rooms" USING "btree" ("id");



CREATE INDEX "ix_event_attendees_id" ON "public"."event_attendees" USING "btree" ("id");



CREATE INDEX "ix_events_id" ON "public"."events" USING "btree" ("id");



CREATE INDEX "ix_events_title" ON "public"."events" USING "btree" ("title");



CREATE INDEX "ix_game_players_id" ON "public"."game_players" USING "btree" ("id");



CREATE INDEX "ix_game_teams_id" ON "public"."game_teams" USING "btree" ("id");



CREATE INDEX "ix_games_id" ON "public"."games" USING "btree" ("id");



CREATE INDEX "ix_sport_group_members_id" ON "public"."sport_group_members" USING "btree" ("id");



CREATE INDEX "ix_sport_groups_id" ON "public"."sport_groups" USING "btree" ("id");



CREATE INDEX "ix_sports_id" ON "public"."sports" USING "btree" ("id");



CREATE INDEX "ix_team_members_id" ON "public"."team_members" USING "btree" ("id");



CREATE INDEX "ix_teams_id" ON "public"."teams" USING "btree" ("id");



CREATE UNIQUE INDEX "ix_users_email" ON "public"."users" USING "btree" ("email");



CREATE INDEX "ix_users_id" ON "public"."users" USING "btree" ("id");



CREATE INDEX "ix_vendor_services_id" ON "public"."vendor_services" USING "btree" ("id");



CREATE INDEX "ix_vendors_business_name" ON "public"."vendors" USING "btree" ("business_name");



CREATE INDEX "ix_vendors_id" ON "public"."vendors" USING "btree" ("id");



ALTER TABLE ONLY "public"."chat_messages"
    ADD CONSTRAINT "chat_messages_chat_room_id_fkey" FOREIGN KEY ("chat_room_id") REFERENCES "public"."chat_rooms"("id");



ALTER TABLE ONLY "public"."chat_messages"
    ADD CONSTRAINT "chat_messages_sender_id_fkey" FOREIGN KEY ("sender_id") REFERENCES "public"."users"("id");



ALTER TABLE ONLY "public"."chat_rooms"
    ADD CONSTRAINT "chat_rooms_event_id_fkey" FOREIGN KEY ("event_id") REFERENCES "public"."events"("id");



ALTER TABLE ONLY "public"."chat_rooms"
    ADD CONSTRAINT "chat_rooms_sport_group_id_fkey" FOREIGN KEY ("sport_group_id") REFERENCES "public"."sport_groups"("id");



ALTER TABLE ONLY "public"."event_attendees"
    ADD CONSTRAINT "event_attendees_event_id_fkey" FOREIGN KEY ("event_id") REFERENCES "public"."events"("id");



ALTER TABLE ONLY "public"."event_attendees"
    ADD CONSTRAINT "event_attendees_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id");



ALTER TABLE ONLY "public"."events"
    ADD CONSTRAINT "events_creator_id_fkey" FOREIGN KEY ("creator_id") REFERENCES "public"."users"("id");



ALTER TABLE ONLY "public"."game_players"
    ADD CONSTRAINT "game_players_game_id_fkey" FOREIGN KEY ("game_id") REFERENCES "public"."games"("id");



ALTER TABLE ONLY "public"."game_players"
    ADD CONSTRAINT "game_players_member_id_fkey" FOREIGN KEY ("member_id") REFERENCES "public"."sport_group_members"("id");



ALTER TABLE ONLY "public"."game_players"
    ADD CONSTRAINT "game_players_team_id_fkey" FOREIGN KEY ("team_id") REFERENCES "public"."game_teams"("id");



ALTER TABLE ONLY "public"."game_teams"
    ADD CONSTRAINT "game_teams_captain_id_fkey" FOREIGN KEY ("captain_id") REFERENCES "public"."sport_group_members"("id");



ALTER TABLE ONLY "public"."game_teams"
    ADD CONSTRAINT "game_teams_game_id_fkey" FOREIGN KEY ("game_id") REFERENCES "public"."games"("id");



ALTER TABLE ONLY "public"."games"
    ADD CONSTRAINT "games_assistant_referee_id_fkey" FOREIGN KEY ("assistant_referee_id") REFERENCES "public"."sport_group_members"("id");



ALTER TABLE ONLY "public"."games"
    ADD CONSTRAINT "games_referee_id_fkey" FOREIGN KEY ("referee_id") REFERENCES "public"."sport_group_members"("id");



ALTER TABLE ONLY "public"."games"
    ADD CONSTRAINT "games_sport_group_id_fkey" FOREIGN KEY ("sport_group_id") REFERENCES "public"."sport_groups"("id");



ALTER TABLE ONLY "public"."sport_group_members"
    ADD CONSTRAINT "sport_group_members_sport_group_id_fkey" FOREIGN KEY ("sport_group_id") REFERENCES "public"."sport_groups"("id");



ALTER TABLE ONLY "public"."sport_group_members"
    ADD CONSTRAINT "sport_group_members_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id");



ALTER TABLE ONLY "public"."sport_groups"
    ADD CONSTRAINT "sport_groups_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."users"("email");



ALTER TABLE ONLY "public"."sport_groups"
    ADD CONSTRAINT "sport_groups_creator_id_fkey" FOREIGN KEY ("creator_id") REFERENCES "public"."users"("id");



ALTER TABLE ONLY "public"."sports"
    ADD CONSTRAINT "sports_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."users"("id");



ALTER TABLE ONLY "public"."team_members"
    ADD CONSTRAINT "team_members_team_id_fkey" FOREIGN KEY ("team_id") REFERENCES "public"."teams"("id");



ALTER TABLE ONLY "public"."team_members"
    ADD CONSTRAINT "team_members_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id");



ALTER TABLE ONLY "public"."teams"
    ADD CONSTRAINT "teams_sport_group_id_fkey" FOREIGN KEY ("sport_group_id") REFERENCES "public"."sport_groups"("id");



ALTER TABLE ONLY "public"."vendor_services"
    ADD CONSTRAINT "vendor_services_vendor_id_fkey" FOREIGN KEY ("vendor_id") REFERENCES "public"."vendors"("id");



ALTER TABLE ONLY "public"."vendors"
    ADD CONSTRAINT "vendors_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id");



ALTER TABLE "public"."users" ENABLE ROW LEVEL SECURITY;




ALTER PUBLICATION "supabase_realtime" OWNER TO "postgres";


GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";








































































































































































GRANT ALL ON TABLE "public"."alembic_version" TO "anon";
GRANT ALL ON TABLE "public"."alembic_version" TO "authenticated";
GRANT ALL ON TABLE "public"."alembic_version" TO "service_role";



GRANT ALL ON TABLE "public"."chat_messages" TO "anon";
GRANT ALL ON TABLE "public"."chat_messages" TO "authenticated";
GRANT ALL ON TABLE "public"."chat_messages" TO "service_role";



GRANT ALL ON SEQUENCE "public"."chat_messages_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."chat_messages_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."chat_messages_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."chat_rooms" TO "anon";
GRANT ALL ON TABLE "public"."chat_rooms" TO "authenticated";
GRANT ALL ON TABLE "public"."chat_rooms" TO "service_role";



GRANT ALL ON SEQUENCE "public"."chat_rooms_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."chat_rooms_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."chat_rooms_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."event_attendees" TO "anon";
GRANT ALL ON TABLE "public"."event_attendees" TO "authenticated";
GRANT ALL ON TABLE "public"."event_attendees" TO "service_role";



GRANT ALL ON SEQUENCE "public"."event_attendees_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."event_attendees_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."event_attendees_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."events" TO "anon";
GRANT ALL ON TABLE "public"."events" TO "authenticated";
GRANT ALL ON TABLE "public"."events" TO "service_role";



GRANT ALL ON SEQUENCE "public"."events_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."events_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."events_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."game_players" TO "anon";
GRANT ALL ON TABLE "public"."game_players" TO "authenticated";
GRANT ALL ON TABLE "public"."game_players" TO "service_role";



GRANT ALL ON SEQUENCE "public"."game_players_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."game_players_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."game_players_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."game_teams" TO "anon";
GRANT ALL ON TABLE "public"."game_teams" TO "authenticated";
GRANT ALL ON TABLE "public"."game_teams" TO "service_role";



GRANT ALL ON SEQUENCE "public"."game_teams_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."game_teams_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."game_teams_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."games" TO "anon";
GRANT ALL ON TABLE "public"."games" TO "authenticated";
GRANT ALL ON TABLE "public"."games" TO "service_role";



GRANT ALL ON SEQUENCE "public"."games_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."games_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."games_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."sport_group_members" TO "anon";
GRANT ALL ON TABLE "public"."sport_group_members" TO "authenticated";
GRANT ALL ON TABLE "public"."sport_group_members" TO "service_role";



GRANT ALL ON SEQUENCE "public"."sport_group_members_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."sport_group_members_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."sport_group_members_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."sport_groups" TO "anon";
GRANT ALL ON TABLE "public"."sport_groups" TO "authenticated";
GRANT ALL ON TABLE "public"."sport_groups" TO "service_role";



GRANT ALL ON TABLE "public"."sports" TO "anon";
GRANT ALL ON TABLE "public"."sports" TO "authenticated";
GRANT ALL ON TABLE "public"."sports" TO "service_role";



GRANT ALL ON SEQUENCE "public"."sports_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."sports_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."sports_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."team_members" TO "anon";
GRANT ALL ON TABLE "public"."team_members" TO "authenticated";
GRANT ALL ON TABLE "public"."team_members" TO "service_role";



GRANT ALL ON SEQUENCE "public"."team_members_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."team_members_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."team_members_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."teams" TO "anon";
GRANT ALL ON TABLE "public"."teams" TO "authenticated";
GRANT ALL ON TABLE "public"."teams" TO "service_role";



GRANT ALL ON SEQUENCE "public"."teams_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."teams_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."teams_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."users" TO "anon";
GRANT ALL ON TABLE "public"."users" TO "authenticated";
GRANT ALL ON TABLE "public"."users" TO "service_role";



GRANT ALL ON SEQUENCE "public"."users_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."vendor_services" TO "anon";
GRANT ALL ON TABLE "public"."vendor_services" TO "authenticated";
GRANT ALL ON TABLE "public"."vendor_services" TO "service_role";



GRANT ALL ON SEQUENCE "public"."vendor_services_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."vendor_services_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."vendor_services_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."vendors" TO "anon";
GRANT ALL ON TABLE "public"."vendors" TO "authenticated";
GRANT ALL ON TABLE "public"."vendors" TO "service_role";



GRANT ALL ON SEQUENCE "public"."vendors_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."vendors_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."vendors_id_seq" TO "service_role";









ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "service_role";






























RESET ALL;
