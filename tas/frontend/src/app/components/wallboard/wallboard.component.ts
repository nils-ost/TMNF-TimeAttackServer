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
import { Router } from "@angular/router";
import { Server } from 'src/app/interfaces/server';
import { ServerService } from 'src/app/services/server.service';

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

  servers: Server[] = [];
  players: Player[] = [];
  settings?: Settings;
  globalRankings: GlobalRanking[] = [];
  challengeRankings: { [key: string]: ChallengeRanking[] } = {};
  challenges: Challenge[] = [];
  currentChallenges: { [key: string]: Challenge } = {};
  nextChallenges: { [key: string]: Challenge } = {};
  switchAutoRefreshSubject: Subject<boolean> = new Subject<boolean>();
  unpredictedUpIn: boolean = true;
  displayPageFoundAtURL: boolean = true;
  time_left: number = 9999;
  lostConnection: boolean = true;

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
    private serverService: ServerService,
    private playerService: PlayerService,
    private rankingService: RankingService,
    private challengeService: ChallengeService,
    private settingsService: SettingsService,
    private router: Router
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
          tooltipLabel: $localize `:Text for link to hide Page-URL Message on bottom of screen@@LinkTextHidePageURL:Hide Page-URL Message`,
          tooltipPosition: "top"
        },
        icon: 'pi pi-minus-circle',
        command: () => {
          this.displayPageFoundAtURL = false;
          this.speeddail_menu.reverse();
          let b = this.speeddail_menu.pop();
          this.speeddail_menu.pop();
          if (b) this.speeddail_menu.push(b);
          this.speeddail_menu.reverse();
        }
      },
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
    for (const server of this.servers) {
      let c_current_id: string | null = this.currentChallenges[server.id].id
      if (c_current_id) {
        this.rankingService
          .getChallengeRankings(c_current_id)
          .subscribe(
            (rankings: ChallengeRanking[]) => {
              this.challengeRankings[server.id] = this.alignChallengeRankings(rankings, server.id);
            }
          )
      }
    }
    this.rankingService
      .getGlobalRankings()
      .subscribe(
        (rankings: GlobalRanking[]) => {
          this.globalRankings = this.alignGlobalRankings(rankings);
        }
      );
  }

  refreshLostConnection() {
    for (const s of this.servers) {
      if (!s.running) {
        this.lostConnection = true;
        return;
      }
      if (s.id in this.currentChallenges && s.id in this.nextChallenges && !this.currentChallenges[s.id].id && !this.nextChallenges[s.id].id) {
        this.lostConnection = true;
        return;
      }
    }
    this.lostConnection = false;
  }

  refreshChallenges() {
    this.challengeService
      .getCurrentChallenges()
      .subscribe(
        (challenges: Challenge[]) => {
          let cc: { [key: string]: Challenge } = {};
          for (const c of challenges) cc[c.server] = c;
          this.currentChallenges = cc;
          this.refreshLostConnection();
          this.refreshRankings();
        }
      );
    this.challengeService
      .getNextChallenges()
      .subscribe(
        (challenges: Challenge[]) => {
          let nc: { [key: string]: Challenge } = {};
          for (const c of challenges) nc[c.server] = c;
          this.nextChallenges = nc;
          this.refreshLostConnection();
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
    this.serverService
      .getServers()
      .subscribe(
        (servers: Server[]) => {
          this.servers = servers;
          this.refreshLostConnection();
        }
      );
    this.settingsService
      .getSettings()
      .subscribe(
        (s: Settings) => {
          this.settings = s;
          if (s.end_time) this.time_left = s.end_time - Math.floor(Date.now()/1000);
          if (s.hotseat_mode) this.router.navigate(['/hotseat-wallboard']);
        }
      );
  }

  alignChallengeRankings(rankings: ChallengeRanking[], for_server: string): ChallengeRanking[] {
    let result: ChallengeRanking[] = [];
    if (this.settings) {
      rankings.sort((a, b) => a.rank - b.rank);
      let i = 0;
      while (i < rankings.length && result.length < Math.min(this.settings['wallboard_players_max'], rankings.length)) {
        if (this.playerActive(rankings[i]['player_id'], for_server)) {
          result.push(rankings[i]);
        }
        i++;
      }
      i = 0;
      while (i < rankings.length && result.length < Math.min(this.settings['wallboard_players_max'], rankings.length)) {
        if (!this.playerActive(rankings[i]['player_id'], for_server)) {
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

  playerActive(player_id: string, for_server: string | null = null): boolean {
    let p = this.players.find(p => p.id === player_id);
    if (p) {
      if ((for_server && p.on_server && p.on_server == for_server) || !for_server)
        return (((Date.now() / 1000) - p.last_update) <= 60);
    }
    return false;
  }

}
