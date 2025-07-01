export interface Sport {
  id: number;
  name: string;
  type: "Team" | "Individual";
  max_players_per_team?: number;
  min_teams?: number;
  players_per_match?: number;
  requires_referee: boolean;
  rules?: any;
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
