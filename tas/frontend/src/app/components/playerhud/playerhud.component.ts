import { Component, OnInit, OnDestroy } from '@angular/core';
import { Player } from '../../interfaces/player';
import { Settings } from '../../interfaces/settings';
import { ChallengeRanking, GlobalRanking, PlayerRanking } from '../../interfaces/ranking';
import { Challenge } from '../../interfaces/challenge';
import { PlayerService } from '../../services/player.service';
import { SettingsService } from '../../services/settings.service';
import { RankingService } from '../../services/ranking.service';
import { ChallengeService } from '../../services/challenge.service';
import { Subscription, timer, Subject } from 'rxjs';
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-playerhud',
  templateUrl: './playerhud.component.html',
  styleUrls: ['./playerhud.component.scss']
})
export class PlayerhudComponent implements OnInit, OnDestroy {
  refreshPlayersTimer = timer(30000, 30000);
  refreshRankingsTimer = timer(10000, 10000);
  refreshPlayersTimerSubscription: Subscription | undefined;
  refreshRankingsTimerSubscription: Subscription | undefined;
  switchAutoRefreshSubscription: Subscription | undefined;
  
  players: Player[] = [];
  filteredPlayers: Player[] = [];
  playerMe?: Player;
  selectedPlayerID?: string;
  settings?: Settings;
  challenges: Challenge[] = [];
  challengeRankings: ChallengeRanking[] = [];
  globalRankings: GlobalRanking[] = [];
  playerRankings: PlayerRanking[] = [];
  currentChallenge?: Challenge;
  meChallengeRank: number | undefined;
  meChallengeDiff: number | undefined;
  meGlobalRank: number | undefined;
  meGlobalDiff: number | undefined;
  bestChallengesNames: string[] = [];
  worstChallengesNames: string[] = [];
  missingChallengesNames: string[] = [];
  bestRank: number | undefined;
  worstRank: number | undefined;
  speeddail_menu: MenuItem[] = [];
  switchAutoRefreshSubject: Subject<boolean> = new Subject<boolean>();

  enable_menu_item: MenuItem = {
    tooltipOptions: {
      tooltipLabel: "Enable AutoRefresh",
      tooltipPosition: "top"
    },
    icon: 'pi pi-refresh',
    command: () => {
      this.switchAutoRefreshSubject.next(true);
    }
  };
  disable_menu_item: MenuItem = {
    tooltipOptions: {
      tooltipLabel: "Disable AutoRefresh",
      tooltipPosition: "top"
    },
    icon: 'pi pi-trash',
    command: () => {
      this.switchAutoRefreshSubject.next(false);
    }
  };

  constructor(
    private playerService: PlayerService,
    private settingsService: SettingsService,
    private rankingService: RankingService,
    private challengeService: ChallengeService
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
          tooltipLabel: "Open Challenges Screen",
          tooltipPosition: "top"
        },
        icon: 'pi pi-list',
        routerLink: ['/challenges']
      },
      {
        tooltipOptions: {
          tooltipLabel: "Open Players Screen",
          tooltipPosition: "top"
        },
        icon: 'pi pi-users',
        routerLink: ['/players']
      },
      {
        tooltipOptions: {
          tooltipLabel: "Open Wallboard",
          tooltipPosition: "top"
        },
        icon: 'pi pi-window-maximize',
        routerLink: ['/wallboard']
      },
      {
        tooltipOptions: {
          tooltipLabel: "Open Home Screen",
          tooltipPosition: "top"
        },
        icon: 'pi pi-home',
        routerLink: ['/']
      }
    ]

    this.refreshSettings();
    this.refreshPlayerMe();
    this.refreshPlayers();
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
        }
      );
  }

  refreshChallenges() {
    this.challengeService
      .getChallenges()
      .subscribe((c: Challenge[]) => {
        this.challenges = c;
        this.buildBestWorstMissingChallenges();
      });
  }

  refreshPlayers() {
    this.playerService
      .getPlayers()
      .subscribe(
        (players: Player[]) => {
          this.players = players;
          this.filteredPlayers = [];
          for(let i = 0; i < players.length; i++) {
            if (!players[i].ip) this.filteredPlayers.push(players[i]);
          }
        }
      );
  }

  refreshPlayerMe() {
    this.playerService
      .getPlayerMe()
      .subscribe(
        (player: Player | null) => {
          if (player) {
            this.playerMe = player;
            this.refreshChallenges();
            this.refreshRankings();
            this.enableAutoRefresh();
          }
          else {
            this.playerMe = undefined;
          }
        }
      );
  }

  applyPlayerMe() {
    if (this.selectedPlayerID) {
      this.playerService
        .setPlayerMe(this.selectedPlayerID)
        .subscribe(() => {
          this.refreshPlayerMe();
        });
    }
  }

  refreshRankings() {
    this.challengeService
      .getChallengeCurrent()
      .subscribe((c: Challenge) => {
        this.currentChallenge = c;
        if (this.currentChallenge) {
          this.rankingService
            .getChallengeRankings(this.currentChallenge.id)
            .subscribe((cr: ChallengeRanking[]) => {
              this.challengeRankings = cr;
              this.rankingService
                .getGlobalRankings()
                .subscribe((gr: GlobalRanking[]) => {
                  this.globalRankings = gr;
                  this.buildMeRanks();
                });
            });
        }
        if (this.playerMe) {
          this.playerService
            .getPlayerRankings(this.playerMe.id)
            .subscribe((pr: PlayerRanking[]) => {
              this.playerRankings = pr;
              this.buildBestWorstMissingChallenges();
            });
        }
      });
  }

  enableAutoRefresh() {
    this.refreshRankingsTimerSubscription = this.refreshRankingsTimer.subscribe(() => this.refreshRankings());
    this.refreshPlayersTimerSubscription = this.refreshPlayersTimer.subscribe(() => this.refreshPlayers());
    this.speeddail_menu.reverse();
    this.speeddail_menu.pop();
    this.speeddail_menu.push(this.disable_menu_item);
    this.speeddail_menu.reverse();
  }

  disableAutoRefresh() {
    this.refreshPlayersTimerSubscription?.unsubscribe();
    this.refreshRankingsTimerSubscription?.unsubscribe();
    this.speeddail_menu.reverse();
    this.speeddail_menu.pop();
    this.speeddail_menu.push(this.enable_menu_item);
    this.speeddail_menu.reverse();
  }

  buildMeRanks() {
    if (this.playerMe) {
      let meCR = this.challengeRankings.find(cr => cr.player_id === this.playerMe!.id);
      if (meCR) {
        this.meChallengeRank = meCR.rank;
        if (meCR.rank > 1) {
          let pCR = this.challengeRankings.find(cr => cr.rank === meCR!.rank - 1);
          if (pCR) this.meChallengeDiff = pCR.time - meCR.time;
          else this.meChallengeDiff = undefined;
        }
        else this.meChallengeDiff = undefined;
      }
      else this.meChallengeRank = undefined;
      let meGR = this.globalRankings.find(gr => gr.player_id === this.playerMe!.id);
      if (meGR) {
        this.meGlobalRank = meGR.rank;
        if (meGR.rank > 1) {
          let pGR = this.globalRankings.find(gr => gr.rank === meGR!.rank - 1);
          if (pGR) this.meGlobalDiff = meGR.points - pGR.points;
          else this.meGlobalDiff = undefined;
        }
      }
      else this.meGlobalRank = undefined;
    }
  }

  buildBestWorstMissingChallenges() {
    let best: number = 9999;
    let worst: number = 0;
    let bestS: string[] = [];
    let worstS: string[] = [];
    for (let i = 0; i < this.playerRankings.length; i++) {
      let pr: PlayerRanking = this.playerRankings[i];
      if (pr.rank > worst) {
        worst = pr.rank;
        worstS = [];
      }
      if (pr.rank === worst) worstS.push(this.getChallengeNameById(pr.challenge_id));
      if (pr.rank < best) {
        best = pr.rank;
        bestS = [];
      }
      if (pr.rank === best) bestS.push(this.getChallengeNameById(pr.challenge_id));
    }

    let missingS: string[] = [];
    for (let i = 0; i < this.challenges.length; i++) {
      let c: Challenge = this.challenges[i];
      let pr = this.playerRankings.find(pr => pr.challenge_id === c.id);
      if (!pr) missingS.push(c.name);
    }

    this.bestChallengesNames = bestS;
    this.worstChallengesNames = worstS;
    this.missingChallengesNames = missingS;
    if (best != 9999) this.bestRank = best;
    else this.bestRank = undefined;
    if (worst != 0) this.worstRank = worst;
    else this.worstRank = undefined;
  }

  getChallengeNameById(challenge_id: string): string {
    let c = this.challenges.find(c => c.id === challenge_id);
    if (c) return c.name;
    else return "--unknown--";
  }
}
