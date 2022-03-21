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
            });
          this.rankingService
            .getGlobalRankings()
            .subscribe((gr: GlobalRanking[]) => {
              this.globalRankings = gr;
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
}
