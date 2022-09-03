export interface Settings {
    wallboard_players_max: number;
    wallboard_challenges_max: number;
    tmnfd_name: string;
    display_self_url: string;
    display_admin: string;
    client_download_url?: string;
    provide_replays: boolean;
    provide_thumbnails: boolean;
    provide_challenges: boolean;
    start_time: number | null;
    end_time: number | null;
}
