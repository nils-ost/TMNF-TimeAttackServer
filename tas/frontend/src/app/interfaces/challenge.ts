export interface Challenge {
  id: string;
  server: string;
  name: string;
  seen_count: number;
  seen_last: number;
  time_limit: number;
}

export interface ChallengeDisplay {
  id: string;
  name: string;
  seen_count: number;
  time_limit: number;
  is_current: boolean;
  is_next: boolean;
  is_loading: boolean;
  up_in: string;
}
