import { Component, OnInit } from '@angular/core';
import { ChallengeService } from '../../services/challenge.service';
import { RankingService } from '../../services/ranking.service';
import { PlayerService } from '../../services/player.service';
import { SettingsService } from '../../services/settings.service';
import { Settings } from '../../interfaces/settings';
import { Challenge } from '../../interfaces/challenge';
import { ChallengeRanking } from '../../interfaces/ranking';
import { PlayerChallengeLaptime } from '../../interfaces/laptime';
import { Player } from '../../interfaces/player';
import { MenuItem } from 'primeng/api';
import { Router } from "@angular/router";
import { Server } from 'src/app/interfaces/server';
import { ServerService } from 'src/app/services/server.service';

@Component({
  selector: 'app-challenges',
  templateUrl: './challenges.component.html',
  styleUrls: ['./challenges.component.scss']
})
export class ChallengesComponent implements OnInit {
  servers: Server[] = [];
  challenges: Challenge[] = [];
  currentChallenges: Challenge[] = [];
  selectedChallenge?: Challenge;
  selectedChallengeRanking?: ChallengeRanking;
  settings?: Settings;
  challengeRankings: ChallengeRanking[] = [];
  playerChallengeLaptimes: PlayerChallengeLaptime[] = [];
  players: Player[] = [];
  provide_replays: boolean = false;
  speeddail_menu: MenuItem[] = [];

  constructor(
    private challengeService: ChallengeService,
    private rankingService: RankingService,
    private playerService: PlayerService,
    private settingsService: SettingsService,
    private serverService: ServerService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.refreshSettings();
    this.refreshServers();
    this.refreshChallenges();
    this.refreshPlayers();

    this.speeddail_menu = [
      {
        tooltipOptions: {
          tooltipLabel: $localize `:Text for link to refresh screen@@LinkTextRefreshScreen:Refresh Screen`,
          tooltipPosition: "top"
        },
        icon: 'pi pi-refresh',
        command: () => {
          this.refreshAll();
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
          tooltipLabel: $localize `:Text for link to open Players Screen@@LinkTextOpenPlayersScreen:Open Players Screen`,
          tooltipPosition: "top"
        },
        icon: 'pi pi-users',
        routerLink: ['/players']
      },
      {
        tooltipOptions: {
          tooltipLabel: $localize `:Text for link to open Wallboard Screen@@LinkTextOpenWallboardScreen:Open Wallboard`,
          tooltipPosition: "top"
        },
        icon: 'pi pi-window-maximize',
        routerLink: ['/wallboard']
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

  selectChallenge(event: any) {
    this.selectedChallengeRanking = undefined;
    this.playerChallengeLaptimes = [];
    if (event) {
      this.selectedChallenge = event.data
      this.refreshChallengeRankings();
    }
    else {
      this.selectedChallenge = undefined;
      this.challengeRankings = [];
    }
  }

  selectChallengeRanking(event: any) {
    if (event) {
      this.selectedChallengeRanking = event.data;
      this.refreshPlayerChallengeLaptimes();
    }
    else {
      this.selectedChallengeRanking = undefined;
      this.playerChallengeLaptimes = [];
    }
  }

  refreshChallenges() {
    this.challengeService
      .getChallenges()
      .subscribe(
        (challenges: Challenge[]) => {
          this.challenges = challenges;
        }
      );
    this.challengeService
      .getCurrentChallenges()
      .subscribe(
        (c: Challenge[]) => {
          this.currentChallenges = c;
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

  refreshChallengeRankings() {
    if (this.selectedChallenge) {
      this.rankingService
        .getChallengeRankings(this.selectedChallenge.id)
        .subscribe(
          (rankings: ChallengeRanking[]) => {
            this.challengeRankings = rankings;
          }
        );
    }
  }

  refreshPlayerChallengeLaptimes() {
    if (this.selectedChallenge && this.selectedChallengeRanking) {
      this.playerService
        .getPlayerChallengeLaptimes(this.selectedChallengeRanking.player_id, this.selectedChallenge.id)
        .subscribe(
          (laptimes: PlayerChallengeLaptime[]) => {
            this.playerChallengeLaptimes = laptimes;
          }
        );
    }
  }

  refreshSettings() {
    this.settingsService
      .getSettings()
      .subscribe(
        (settings: Settings) => {
          this.settings = settings;
          this.provide_replays = settings.provide_replays;
          if (settings.hotseat_mode) this.router.navigate(['/players']);
        }
      );
  }

  refreshServers() {
    this.serverService
      .getServers()
      .subscribe(
        (servers: Server[]) => {
          this.servers = servers;
        }
      );
  }

  refreshAll() {
    this.refreshServers();
    this.refreshChallenges();
    this.refreshPlayers();
    this.refreshChallengeRankings();
    this.refreshPlayerChallengeLaptimes();
  }

}
