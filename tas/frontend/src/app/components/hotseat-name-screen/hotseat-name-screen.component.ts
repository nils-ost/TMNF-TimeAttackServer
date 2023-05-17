import { Component, OnDestroy, OnInit } from '@angular/core';
import { Player } from 'src/app/interfaces/player';
import { Settings } from 'src/app/interfaces/settings';
import { PlayerService } from 'src/app/services/player.service';
import { SettingsService } from 'src/app/services/settings.service';
import { Subscription, timer } from 'rxjs';
import { ChallengeService } from 'src/app/services/challenge.service';
import { Challenge } from 'src/app/interfaces/challenge';
import { RankingService } from 'src/app/services/ranking.service';
import { ChallengeRanking } from 'src/app/interfaces/ranking';
import { Router } from "@angular/router";
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-hotseat-name-screen',
  templateUrl: './hotseat-name-screen.component.html',
  styleUrls: ['./hotseat-name-screen.component.scss']
})
export class HotseatNameScreenComponent implements OnInit, OnDestroy {
  refreshPlayerHotseatTimer = timer(5000, 5000);
  refreshRankingsTimer = timer(10000, 10000);
  refreshPlayersTimer = timer(30000, 30000);
  refreshPlayerHotseatTimerSubscription: Subscription | undefined;
  refreshRankingsTimerSubscription: Subscription | undefined;
  refreshPlayersTimerSubscription: Subscription | undefined;

  players: Player[] = [];
  playerHotseat?: Player;
  settings?: Settings;
  newPlayerName: string = "";
  currentChallenge?: Challenge;
  challengeRankings: ChallengeRanking[] = [];
  meChallengeRank: number | undefined;
  meChallengeDiff: number | undefined;
  speeddail_menu: MenuItem[] = [];

  constructor(
    private playerService: PlayerService,
    private settingsService: SettingsService,
    private challengeService: ChallengeService,
    private rankingService: RankingService,
    private router: Router
  ) { }

  ngOnInit(): void {
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
          tooltipLabel: $localize `:Text for link to open Wallboard Screen@@LinkTextOpenWallboardScreen:Open Wallboard`,
          tooltipPosition: "top"
        },
        icon: 'pi pi-window-maximize',
        routerLink: ['/hotseat-wallboard']
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
    this.refreshPlayerHotseat();
    this.refreshRankings();
    this.enableAutoRefresh();
  }

  ngOnDestroy(): void {
    this.disableAutoRefresh();
  }

  refreshSettings() {
    this.settingsService
      .getSettings()
      .subscribe(
        (settings: Settings) => {
          this.settings = settings
          if (!settings.hotseat_mode) this.router.navigate(['/playerhud']);
        }
      );
  }

  refreshPlayerHotseat() {
    this.playerService
      .getPlayerHotseat()
      .subscribe(
        (player: Player | null) => {
          if (player) {
            this.playerHotseat = player;
          }
          else {
            this.playerHotseat = undefined;
          }
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
    this.challengeService
      .getChallengeCurrent()
      .subscribe((c: Challenge | null) => {
        if (c) {
          this.currentChallenge = c;
          this.rankingService
            .getChallengeRankings(c.id)
            .subscribe((cr: ChallengeRanking[]) => {
              this.challengeRankings = cr;
              this.buildMeRanks();
            });
        }
        else this.currentChallenge = undefined;
      });
  }

  enableAutoRefresh() {
    this.refreshRankingsTimerSubscription = this.refreshRankingsTimer.subscribe(() => this.refreshRankings());
    this.refreshPlayerHotseatTimerSubscription = this.refreshPlayerHotseatTimer.subscribe(() => this.refreshPlayerHotseat());
    this.refreshPlayersTimerSubscription = this.refreshPlayersTimer.subscribe(() => this.refreshPlayers());
  }

  disableAutoRefresh() {
    this.refreshRankingsTimerSubscription?.unsubscribe();
    this.refreshPlayerHotseatTimerSubscription?.unsubscribe();
    this.refreshPlayersTimerSubscription?.unsubscribe();
  }

  sendPlayerHotseat() {
    if (this.newPlayerName != "") {
      this.playerService
        .setPlayerHotseat(this.newPlayerName)
        .subscribe(() => {
          this.refreshPlayers();
          this.refreshPlayerHotseat();
          this.newPlayerName = "";
        });
    }
  }

  buildMeRanks() {
    if (this.playerHotseat) {
      let meCR = this.challengeRankings.find(cr => cr.player_id === this.playerHotseat!.id);
      if (meCR) {
        this.meChallengeRank = meCR.rank;
        let pCR = undefined;
        if (meCR.rank > 1) pCR = this.challengeRankings.find(cr => cr.rank === meCR!.rank - 1);
        else pCR = this.challengeRankings.find(cr => cr.rank === 2);
        if (pCR) this.meChallengeDiff = pCR.time - meCR.time;
        else this.meChallengeDiff = undefined;
      }
      else this.meChallengeRank = undefined;
    }
  }

}
