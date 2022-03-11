export interface GlobalRanking {
    player_id: string;
    rank: number;
    points: number;
}

export interface ChallengeRanking {
    player_id: string;
    time: number;
    rank: number;
    points: number;
    at: number;
}

export interface PlayerRanking {
    challenge_id: string;
    time: number;
    rank: number;
    points: number;
    at: number;
}
