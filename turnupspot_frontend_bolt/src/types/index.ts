export type Sport = 'Football' | 'Basketball' | 'Tennis' | 'AmericanFootball';

export interface SportGroup {
  id: string;
  name: string;
  sport: Sport;
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
  role: 'admin' | 'member';
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
  status: 'scheduled' | 'in-progress' | 'completed';
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