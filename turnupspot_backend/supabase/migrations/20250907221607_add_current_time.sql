-- Remove the playing_days column from sport_groups table (it's handled by PlayingDay model)
ALTER TABLE sport_groups DROP COLUMN IF EXISTS playing_days;

-- Fix game_start_time and game_end_time column types to match Pydantic model
ALTER TABLE sport_groups ALTER COLUMN game_start_time TYPE TIME USING game_start_time::TIME;
ALTER TABLE sport_groups ALTER COLUMN game_end_time TYPE TIME USING game_end_time::TIME;

-- Add the missing current_time column that your SQLAlchemy model expects (quote the column name)
ALTER TABLE games ADD COLUMN "current_time" INTEGER DEFAULT 0;

-- Copy existing game_time values to current_time (if you want to preserve data)
UPDATE games SET "current_time" = COALESCE(game_time, 0);