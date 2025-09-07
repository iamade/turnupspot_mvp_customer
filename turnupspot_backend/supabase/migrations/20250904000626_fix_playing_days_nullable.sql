-- Make playing_days column nullable in sport_groups table
ALTER TABLE sport_groups ALTER COLUMN playing_days DROP NOT NULL;