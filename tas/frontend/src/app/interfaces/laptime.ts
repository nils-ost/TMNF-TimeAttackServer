export interface PlayerLaptime {
    challenge_id: string;
    time: number;
    created_at: number;
    replay?: string;
}

export interface PlayerChallengeLaptime {
    time: number;
    created_at: number;
    replay?: string;
}
