import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription, timer } from 'rxjs';
import { Challenge } from 'src/app/interfaces/challenge';
import { Player } from 'src/app/interfaces/player';
import { ChallengeRanking } from 'src/app/interfaces/ranking';
import { Settings } from 'src/app/interfaces/settings';
import { ChallengeService } from 'src/app/services/challenge.service';
import { PlayerService } from 'src/app/services/player.service';
import { RankingService } from 'src/app/services/ranking.service';
import { SettingsService } from 'src/app/services/settings.service';

@Component({
  selector: 'app-hotseat-wallboard-screen',
  templateUrl: './hotseat-wallboard-screen.component.html',
  styleUrls: ['./hotseat-wallboard-screen.component.scss']
})
export class HotseatWallboardScreenComponent implements OnInit {
  refreshPlayersTimer = timer(30000, 30000);
  refreshCurrentChallengeTimer = timer(5000, 5000);
  refreshSettingsTimer = timer(60000, 60000);
  refreshRankingsTimer = timer(10000, 10000);
  refreshPlayersTimerSubscription: Subscription | undefined;
  refreshCurrentChallengeTimerSubscription: Subscription | undefined;
  refreshSettingsTimerSubscription: Subscription | undefined;
  refreshRankingsTimerSubscription: Subscription | undefined;
  
  settings?: Settings;
  c_current?: Challenge;
  players: Player[] = [];
  challengeRankings: ChallengeRanking[] = [];
  numRows: number = 2;

  constructor(
    private settingsService: SettingsService,
    private playerService: PlayerService,
    private challengeService: ChallengeService,
    private rankingService: RankingService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.enableAutoRefresh();
    this.refreshSettings();
    this.refreshCurrentChallenge();
    this.refreshPlayers();
    this.refreshRankings();
  }

  enableAutoRefresh() {
    this.refreshSettingsTimerSubscription = this.refreshSettingsTimer.subscribe(() => this.refreshSettings());
    this.refreshCurrentChallengeTimerSubscription = this.refreshCurrentChallengeTimer.subscribe(() => this.refreshCurrentChallenge);
    this.refreshPlayersTimerSubscription = this.refreshPlayersTimer.subscribe(() => this.refreshPlayers());
    this.refreshRankingsTimerSubscription = this.refreshRankingsTimer.subscribe(() => this.refreshRankings());
  }

  disableAutoRefresh() {
    this.refreshPlayersTimerSubscription?.unsubscribe();
    this.refreshCurrentChallengeTimerSubscription?.unsubscribe();
    this.refreshSettingsTimerSubscription?.unsubscribe();
    this.refreshRankingsTimerSubscription?.unsubscribe();
  }

  refreshSettings() {
    this.settingsService
      .getSettings()
      .subscribe(
        (settings: Settings) => {
          this.settings = settings;
          if (!settings.hotseat_mode) this.router.navigate(['/wallboard']);
        }
      );
  }

  refreshPlayers() {
    this.playerService
      .getPlayers()
      .subscribe(
        (players: Player[]) => {
          this.players = players;
        }
      );
  }

  refreshRankings() {
    if (this.c_current) {
      this.rankingService
        .getChallengeRankings(this.c_current.id)
        .subscribe(
          (rankings: ChallengeRanking[]) => {
            this.challengeRankings = this.alignChallengeRankings(rankings);
          }
        );
    }
  }

  refreshCurrentChallenge() {
    this.challengeService
      .getChallengeCurrent()
      .subscribe(
        (c: Challenge | null) => {
          if (c) {
            this.c_current = c;
            this.refreshCurrentChallengeTimerSubscription?.unsubscribe();
          }
          else this.c_current = undefined;
        }
      );
  }

  alignChallengeRankings(rankings: ChallengeRanking[]): ChallengeRanking[] {
    let result: ChallengeRanking[] = [];
    if (this.settings) {
      let max_display_players = this.settings['wallboard_players_max'];  // TODO: add some max_row_count value here
      rankings.sort((a, b) => a.rank - b.rank);
      if (rankings.length <= max_display_players) return rankings;
      let i = 0;
      while (i < rankings.length && result.length < Math.min(max_display_players, rankings.length)) {
        if (this.playerActive(rankings[i]['player_id'])) {
          result.push(rankings[i]);
        }
        i++;
      }
      i = 0;
      while (i < rankings.length && result.length < Math.min(max_display_players, rankings.length)) {
        if (!this.playerActive(rankings[i]['player_id'])) {
          result.push(rankings[i]);
        }
        i++;
      }
      result.sort((a, b) => a.rank - b.rank);
    }
    return result;
  }

  playerActive(player_id: string): boolean {
    let p = this.players.find(p => p.id === player_id);
    if (p) return (((Date.now() / 1000) - p.last_update) <= 60);
    else return false;
  }

}
