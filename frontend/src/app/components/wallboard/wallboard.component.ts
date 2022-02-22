import { Component, OnInit } from '@angular/core';
import { Player } from '../../interfaces/player';
import { GlobalRanking } from '../../interfaces/ranking';
import { Challenge } from '../../interfaces/challenge';
import { PlayerService } from '../../services/player.service';
import { RankingService } from '../../services/ranking.service';
import { ChallengeService } from '../../services/challenge.service';
import { Subscription, timer } from 'rxjs';

@Component({
  selector: 'app-wallboard',
  templateUrl: './wallboard.component.html',
  styleUrls: ['./wallboard.component.css']
})
export class WallboardComponent implements OnInit {
  refreshPlayersTimer = timer(30000, 30000);
  refreshRankingsTimer = timer(10000, 10000);
  refreshChallengesTimer = timer(10000, 10000);
  refreshPlayersTimerSubscription: Subscription | undefined;
  refreshRankingsTimerSubscription: Subscription | undefined;
  refreshChallengesTimerSubscription: Subscription | undefined;

  players: Player[] = [];
  globalRankings: GlobalRanking[] = [];
  challenges: Challenge[] = [];
  c_current!: Challenge;
  c_next!: Challenge;

  constructor(
    private playerService: PlayerService,
    private rankingService: RankingService,
    private challengeService: ChallengeService
  ) { }

  ngOnInit(): void {
    this.refreshPlayers();
    this.refreshRankings();
    this.refreshChallenges();
    this.enableAutoRefresh();
  }

  enableAutoRefresh() {
    this.refreshPlayersTimerSubscription = this.refreshPlayersTimer.subscribe(() => this.refreshPlayers());
    this.refreshRankingsTimerSubscription = this.refreshRankingsTimer.subscribe(() => this.refreshRankings());
    this.refreshChallengesTimerSubscription = this.refreshChallengesTimer.subscribe(() => this.refreshChallenges());
  }

  disableAutoRefresh() {
    this.refreshPlayersTimerSubscription?.unsubscribe();
    this.refreshRankingsTimerSubscription?.unsubscribe();
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
    this.rankingService
      .getGlobalRankings()
      .subscribe(
        (rankings: GlobalRanking[]) => {
          this.globalRankings = rankings;
        }
      );
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
      .getChallengeCurrent()
      .subscribe(
        (c: Challenge) => {
          this.c_current = c;
        }
      );
    this.challengeService
      .getChallengeNext()
      .subscribe(
        (c: Challenge) => {
          this.c_next = c;
        }
      );
  }

}
