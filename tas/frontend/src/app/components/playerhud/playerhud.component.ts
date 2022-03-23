import { Component, OnInit, OnDestroy } from '@angular/core';
import { Player } from '../../interfaces/player';
import { Settings } from '../../interfaces/settings';
import { ChallengeRanking, GlobalRanking, PlayerRanking } from '../../interfaces/ranking';
import { Challenge } from '../../interfaces/challenge';
import { PlayerService } from '../../services/player.service';
import { SettingsService } from '../../services/settings.service';
import { RankingService } from '../../services/ranking.service';
import { ChallengeService } from '../../services/challenge.service';
import { Subscription, timer } from 'rxjs';

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

  constructor(
    private playerService: PlayerService,
    private settingsService: SettingsService,
    private rankingService: RankingService,
    private challengeService: ChallengeService
  ) { }

  ngOnInit(): void {
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
            this.refreshSettings();
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
            });
        }
      });
  }

  enableAutoRefresh() {
    this.refreshRankingsTimerSubscription = this.refreshRankingsTimer.subscribe(() => this.refreshRankings());
    this.refreshPlayersTimerSubscription = this.refreshPlayersTimer.subscribe(() => this.refreshPlayers());
  }

  disableAutoRefresh() {
    this.refreshPlayersTimerSubscription?.unsubscribe();
    this.refreshRankingsTimerSubscription?.unsubscribe();
  }

  buildMeRanks() {
    if (this.playerMe) {
      let meCR = this.challengeRankings.find(cr => cr.player_id === this.playerMe!.id);
      if (meCR) {
        this.meChallengeRank = meCR.rank;
        if (meCR.rank > 1) {
          let pCR = this.challengeRankings.find(cr => cr.rank === meCR!.rank - 1);
          if (pCR) this.meChallengeDiff = meCR.time - pCR.time;
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
}
