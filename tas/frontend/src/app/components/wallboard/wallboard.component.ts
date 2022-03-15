import { Component, OnInit, OnDestroy } from '@angular/core';
import { Player } from '../../interfaces/player';
import { GlobalRanking, ChallengeRanking } from '../../interfaces/ranking';
import { Challenge } from '../../interfaces/challenge';
import { Settings } from '../../interfaces/settings';
import { PlayerService } from '../../services/player.service';
import { RankingService } from '../../services/ranking.service';
import { ChallengeService } from '../../services/challenge.service';
import { SettingsService } from '../../services/settings.service';
import { Subscription, timer, Subject } from 'rxjs';
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-wallboard',
  templateUrl: './wallboard.component.html',
  styleUrls: ['./wallboard.component.scss']
})
export class WallboardComponent implements OnInit, OnDestroy {
  refreshPlayersTimer = timer(30000, 30000);
  refreshChallengesTimer = timer(10000, 10000);
  refreshSettingsTimer = timer(60000, 60000);
  refreshPlayersTimerSubscription: Subscription | undefined;
  refreshChallengesTimerSubscription: Subscription | undefined;
  refreshSettingsTimerSubscription: Subscription | undefined;
  switchAutoRefreshSubscription: Subscription | undefined;

  players: Player[] = [];
  settings!: Settings;
  globalRankings: GlobalRanking[] = [];
  challengeRankings: ChallengeRanking[] = [];
  challenges: Challenge[] = [];
  c_current!: Challenge;
  c_next!: Challenge;
  switchAutoRefreshSubject: Subject<boolean> = new Subject<boolean>();

  speeddail_menu: MenuItem[] = [];

  constructor(
    private playerService: PlayerService,
    private rankingService: RankingService,
    private challengeService: ChallengeService,
    private settingsService: SettingsService
  ) { }

  ngOnInit(): void {
    this.refreshSettings();
    this.refreshPlayers();
    this.refreshChallenges();
    this.enableAutoRefresh();

    this.switchAutoRefreshSubscription = this.switchAutoRefreshSubject.subscribe(
      (switchOn) => {
        if (switchOn) this.enableAutoRefresh();
        else this.disableAutoRefresh();
      }
    );

    this.speeddail_menu = [
        {
            tooltipOptions: {
                tooltipLabel: "Enable AutoRefresh",
                tooltipPosition: "top"
            },
            icon: 'pi pi-refresh',
            command: () => {
                this.switchAutoRefreshSubject.next(true);
            }
        },
        {
            tooltipOptions: {
                tooltipLabel: "Disable AutoRefresh",
                tooltipPosition: "top"
            },
            icon: 'pi pi-trash',
            command: () => {
                this.switchAutoRefreshSubject.next(false);
            }
        },
        {
            tooltipOptions: {
                tooltipLabel: "Open Players Screen",
                tooltipPosition: "top"
            },
            icon: 'pi pi-user',
            routerLink: ['/players']
        }
    ]
  }

  ngOnDestroy(): void {
    this.disableAutoRefresh();
    this.switchAutoRefreshSubscription?.unsubscribe();
  }

  enableAutoRefresh() {
    this.refreshPlayersTimerSubscription = this.refreshPlayersTimer.subscribe(() => this.refreshPlayers());
    this.refreshChallengesTimerSubscription = this.refreshChallengesTimer.subscribe(() => this.refreshChallenges());
    this.refreshSettingsTimerSubscription = this.refreshSettingsTimer.subscribe(() => this.refreshSettings());
  }

  disableAutoRefresh() {
    this.refreshPlayersTimerSubscription?.unsubscribe();
    this.refreshChallengesTimerSubscription?.unsubscribe();
    this.refreshSettingsTimerSubscription?.unsubscribe();
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
            this.rankingService
              .getGlobalRankings()
              .subscribe(
                (rankings: GlobalRanking[]) => {
                  this.globalRankings = this.alignGlobalRankings(rankings);
                }
              );
          }
        );
    }
    else {
      this.challengeRankings = [];
      this.rankingService
        .getGlobalRankings()
        .subscribe(
          (rankings: GlobalRanking[]) => {
            this.globalRankings = this.alignGlobalRankings(rankings);
          }
        );
    }
  }

  refreshChallenges() {
    this.challengeService
      .getChallengeCurrent()
      .subscribe(
        (c: Challenge) => {
          this.c_current = c;
          this.challengeService
            .getChallengeNext()
            .subscribe(
              (c: Challenge) => {
                this.c_next = c;
              }
            );
          this.challengeService
            .getChallenges()
            .subscribe(
              (challenges: Challenge[]) => {
                this.challenges = challenges;
              }
            );
          this.refreshRankings();
        }
      );
  }

  refreshSettings() {
    this.settingsService
      .getSettings()
      .subscribe(
        (s: Settings) => {
          this.settings = s;
        }
      );
  }

  alignChallengeRankings(rankings: ChallengeRanking[]): ChallengeRanking[] {
    rankings.sort((a, b) => a.rank - b.rank);
    let result: ChallengeRanking[] = [];
    let i = 0;
    while (i < rankings.length && result.length < Math.min(this.settings['wallboard_players_max'], rankings.length)) {
      if (this.playerActive(rankings[i]['player_id'])) {
        result.push(rankings[i]);
      }
      i++;
    }
    i = 0;
    while (i < rankings.length && result.length < Math.min(this.settings['wallboard_players_max'], rankings.length)) {
      if (!this.playerActive(rankings[i]['player_id'])) {
        result.push(rankings[i]);
      }
      i++;
    }
    result.sort((a, b) => a.rank - b.rank);
    return result;
  }

  alignGlobalRankings(rankings: GlobalRanking[]): GlobalRanking[] {
    rankings.sort((a, b) => a.rank - b.rank);
    let result: GlobalRanking[] = [];
    let i = 0;
    while (i < rankings.length && result.length < Math.min(this.settings['wallboard_players_max'], rankings.length)) {
      if (this.playerActive(rankings[i]['player_id'])) {
        result.push(rankings[i]);
      }
      i++;
    }
    i = 0;
    while (i < rankings.length && result.length < Math.min(this.settings['wallboard_players_max'], rankings.length)) {
      if (!this.playerActive(rankings[i]['player_id'])) {
        result.push(rankings[i]);
      }
      i++;
    }
    result.sort((a, b) => a.rank - b.rank);
    return result;
  }

  playerActive(player_id: string): boolean {
    let p = this.players.find(p => p.id === player_id);
    if (p) return (((Date.now() / 1000) - p.last_update) <= 60);
    else return false;
  }

}