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
  settings?: Settings;
  globalRankings: GlobalRanking[] = [];
  challengeRankings: ChallengeRanking[] = [];
  challenges: Challenge[] = [];
  c_current?: Challenge;
  c_next?: Challenge;
  switchAutoRefreshSubject: Subject<boolean> = new Subject<boolean>();
  unpredictedUpIn: boolean = true;

  speeddail_menu: MenuItem[] = [];
  enable_menu_item: MenuItem = {
    tooltipOptions: {
      tooltipLabel: $localize `:Text for link to enable autorefresh@@LinkTextEnableAutorefresh:Enable AutoRefresh`,
      tooltipPosition: "top"
    },
    icon: 'pi pi-refresh',
    command: () => {
      this.switchAutoRefreshSubject.next(true);
    }
  };
  disable_menu_item: MenuItem = {
    tooltipOptions: {
      tooltipLabel: $localize `:Text for link to disable autorefresh@@LinkTextDisableAutorefresh:Disable AutoRefresh`,
      tooltipPosition: "top"
    },
    icon: 'pi pi-trash',
    command: () => {
      this.switchAutoRefreshSubject.next(false);
    }
  };

  constructor(
    private playerService: PlayerService,
    private rankingService: RankingService,
    private challengeService: ChallengeService,
    private settingsService: SettingsService
  ) { }

  ngOnInit(): void {
    this.switchAutoRefreshSubscription = this.switchAutoRefreshSubject.subscribe(
      (switchOn) => {
        if (switchOn) this.enableAutoRefresh();
        else this.disableAutoRefresh();
      }
    );

    this.speeddail_menu = [
      this.enable_menu_item,
      {
        tooltipOptions: {
          tooltipLabel: $localize `:Text for link to open PlayerHUD@@LinkTextOpenPlayerHUD:Open PlayerHUD`,
          tooltipPosition: "top"
        },
        icon: 'pi pi-user',
        routerLink: ['/playerhud']
      },
      {
        tooltipOptions: {
          tooltipLabel: $localize `:Text for link to open Challenges Screen@@LinkTextOpenChallengesScreen:Open Challenges Screen`,
          tooltipPosition: "top"
        },
        icon: 'pi pi-list',
        routerLink: ['/challenges']
      },
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
          tooltipLabel: $localize `:Text for link to open Home Screen@@LinkTextOpenHomeScreen:Open Home Screen`,
          tooltipPosition: "top"
        },
        icon: 'pi pi-home',
        routerLink: ['/']
      }
    ]

    this.refreshSettings();
    this.refreshPlayers();
    this.refreshChallenges();
    this.enableAutoRefresh();
  }

  ngOnDestroy(): void {
    this.disableAutoRefresh();
    this.switchAutoRefreshSubscription?.unsubscribe();
  }

  enableAutoRefresh() {
    this.refreshPlayersTimerSubscription = this.refreshPlayersTimer.subscribe(() => this.refreshPlayers());
    this.refreshChallengesTimerSubscription = this.refreshChallengesTimer.subscribe(() => this.refreshChallenges());
    this.refreshSettingsTimerSubscription = this.refreshSettingsTimer.subscribe(() => this.refreshSettings());
    this.speeddail_menu.reverse();
    this.speeddail_menu.pop();
    this.speeddail_menu.push(this.disable_menu_item);
    this.speeddail_menu.reverse();
  }

  disableAutoRefresh() {
    this.refreshPlayersTimerSubscription?.unsubscribe();
    this.refreshChallengesTimerSubscription?.unsubscribe();
    this.refreshSettingsTimerSubscription?.unsubscribe();
    this.speeddail_menu.reverse();
    this.speeddail_menu.pop();
    this.speeddail_menu.push(this.enable_menu_item);
    this.speeddail_menu.reverse();
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
    this.rankingService
      .getGlobalRankings()
      .subscribe(
        (rankings: GlobalRanking[]) => {
          this.globalRankings = this.alignGlobalRankings(rankings);
        }
      );
  }

  refreshChallenges() {
    this.challengeService
      .getChallengeCurrent()
      .subscribe(
        (c: Challenge | null) => {
          if (c) this.c_current = c;
          else this.c_current = undefined;
          this.refreshRankings();
        }
      );
    this.challengeService
      .getChallengeNext()
      .subscribe(
        (c: Challenge | null) => {
          if (c) this.c_next = c;
          else this.c_next = undefined;
        }
      );
    this.challengeService
      .getChallenges()
      .subscribe(
        (challenges: Challenge[]) => {
          this.challenges = challenges;
          let c = this.challenges.find(c => c.seen_count === 0);
          if (c) this.unpredictedUpIn = true;
          else this.unpredictedUpIn = false;
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
    let result: ChallengeRanking[] = [];
    if (this.settings) {
      rankings.sort((a, b) => a.rank - b.rank);
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
    }
    return result;
  }

  alignGlobalRankings(rankings: GlobalRanking[]): GlobalRanking[] {
    let result: GlobalRanking[] = [];
    if (this.settings) {
      rankings.sort((a, b) => a.rank - b.rank);
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
    }
    return result;
  }

  playerActive(player_id: string): boolean {
    let p = this.players.find(p => p.id === player_id);
    if (p) return (((Date.now() / 1000) - p.last_update) <= 60);
    else return false;
  }

}
