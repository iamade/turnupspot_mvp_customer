export interface Sport {
  id: number;
  name: string;
  type: "Team" | "Individual";
  max_players_per_team?: number;
  min_teams?: number;
  players_per_match?: number;
  requires_referee: boolean;
  rules?: Record<string, unknown>;
  is_default: boolean;
  created_by?: number;
  created_at: string;
  updated_at?: string;
}

export interface SportGroup {
  id: string;
  name: string;
  sport: string; // Keep as string for now, can be updated later
  description: string;
  location: string;
  venueImage: string;
  adminIds: string[];
  members: Member[];
  playingDates: PlayingDate[];
  createdAt: string;
  updatedAt: string;
}

export interface Member {
  id: string;
  userId: string;
  name: string;
  role: "admin" | "member";
  joinedAt: string;
}

export interface PlayingDate {
  id: string;
  date: string;
  startTime: string;
  endTime: string;
  location: string;
  teams: Team[];
  referee?: Member;
  assistantReferee?: Member;
  status: "scheduled" | "in-progress" | "completed";
}

export interface Team {
  id: string;
  name: string;
  members: Member[];
  isPermanent: boolean;
  stats: TeamStats;
}

export interface TeamStats {
  wins: number;
  losses: number;
  draws: number;
  goalsScored: number;
  goalsConceded: number;
  points: number;
}

export interface AvailableTeam {
  id: string;
  name: string;
  team_number: number;
  captain_id?: number;
  player_count?: number;
}

export enum CoinTossType {
  DRAW_DECIDER = "draw_decider",
  STARTING_TEAM = "starting_team",
}

export interface Match {
  id?: string;
  team_a_id: string;
  team_b_id: string;
  team_a_name?: string;
  team_b_name?: string;
  team_a_score?: number;
  team_b_score?: number;
  winner_id?: string;
  is_draw?: boolean;
  referee_id?: number;
  completed_at?: string;
  started_at?: string;
  requires_coin_toss?: boolean;
  coin_toss_type?: CoinTossType;
  coin_toss_winner_id?: string;
  coin_toss_performed_at?: string;
}

export interface Game {
  id: string;
  sport_group_id: string;
  date: string;
  status: "scheduled" | "in-progress" | "completed";
  matches: Match[];
  current_match?: Match;
  upcoming_match?: {
    team_a_id: string;
    team_b_id: string;
    team_a_name: string;
    team_b_name: string;
    requires_coin_toss?: boolean;
    coin_toss_type?: CoinTossType;
    is_knockout_stage?: boolean;
  };
  coin_toss_state?: {
    pending?: boolean;
    team_a_id?: string;
    team_b_id?: string;
    coin_toss_type?: CoinTossType;
    result?: string;
    winner?: string;
    loser?: string;
  };
  referee: number | null;
  teams: Team[];
  available_teams: AvailableTeam[];
  can_control_match: boolean;
  is_knockout_stage?: boolean;
}
