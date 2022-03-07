export interface GlobalRanking {
    player_id: string;
    rank: number;
    points: number;
}

export interface ChallengeRanking {
    player_id: string;
    time: number;
    rank: number;
    point: number;
    at: number;
}
