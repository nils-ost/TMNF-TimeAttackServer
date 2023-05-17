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
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-hotseat-wallboard-screen',
  templateUrl: './hotseat-wallboard-screen.component.html',
  styleUrls: ['./hotseat-wallboard-screen.component.scss']
})
export class HotseatWallboardScreenComponent implements OnInit {
  refreshPlayersTimer = timer(30000, 30000);
  refreshCurrentChallengeTimer = timer(5000, 5000);
  refreshSettingsTimer = timer(20000, 20000);
  refreshRankingsTimer = timer(10000, 10000);
  refreshPlayersTimerSubscription: Subscription | undefined;
  refreshCurrentChallengeTimerSubscription: Subscription | undefined;
  refreshSettingsTimerSubscription: Subscription | undefined;
  refreshRankingsTimerSubscription: Subscription | undefined;
  
  settings?: Settings;
  c_current?: Challenge;
  players: Player[] = [];
  challengeRankings: ChallengeRanking[] = [];
  numTables: number = 2;
  speeddail_menu: MenuItem[] = [];

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

    this.speeddail_menu = [
      {
        tooltipOptions: {
          tooltipLabel: $localize `:Text for link to open Players Screen@@LinkTextOpenPlayersScreen:Open Players Screen`,
          tooltipPosition: "top"
        },
        icon: 'pi pi-users',
        routerLink: ['/players']
      },
      {
        tooltipOptions: {
          tooltipLabel: $localize `:Text for link to open Hotseat Screen@@LinkTextOpenHotseatNameScreen:Open Hotseat Screen`,
          tooltipPosition: "top"
        },
        icon: 'pi pi-user',
        routerLink: ['/hotseat-name']
      },
      {
        tooltipOptions: {
          tooltipLabel: $localize `:Text for link to open Home Screen@@LinkTextOpenHomeScreen:Open Home Screen`,
          tooltipPosition: "top"
        },
        icon: 'pi pi-home',
        routerLink: ['/']
      }
    ]
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
            this.refreshRankings();
          }
          else this.c_current = undefined;
        }
      );
  }

  alignChallengeRankings(rankings: ChallengeRanking[]): ChallengeRanking[] {
    let result: ChallengeRanking[] = [];
    if (this.settings) {
      let numTables = Math.min(Math.ceil(rankings.length / this.settings.wallboard_players_max), this.settings.wallboard_tables_max);
      this.numTables = Math.max(numTables, 2);  // Allways display at least two tables
      let max_display_players = this.settings.wallboard_players_max * this.numTables;
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
