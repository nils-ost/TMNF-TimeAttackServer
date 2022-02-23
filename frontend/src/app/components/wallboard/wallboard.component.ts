import { Component, OnInit } from '@angular/core';
import { Player } from '../../interfaces/player';
import { GlobalRanking, ChallengeRanking } from '../../interfaces/ranking';
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
  refreshChallengesTimer = timer(10000, 10000);
  refreshPlayersTimerSubscription: Subscription | undefined;
  refreshChallengesTimerSubscription: Subscription | undefined;

  players: Player[] = [];
  globalRankings: GlobalRanking[] = [];
  challengeRankings: ChallengeRanking[] = [];
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
    this.refreshChallenges();
    this.enableAutoRefresh();
  }

  enableAutoRefresh() {
    this.refreshPlayersTimerSubscription = this.refreshPlayersTimer.subscribe(() => this.refreshPlayers());
    this.refreshChallengesTimerSubscription = this.refreshChallengesTimer.subscribe(() => this.refreshChallenges());
  }

  disableAutoRefresh() {
    this.refreshPlayersTimerSubscription?.unsubscribe();
    this.refreshChallengesTimerSubscription?.unsubscribe();
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
            this.rankingService
              .getGlobalRankings()
              .subscribe(
                (rankings: GlobalRanking[]) => {
                  rankings.sort((a, b) => a.rank - b.rank);
                  this.globalRankings = rankings;
                }
              );
            rankings.sort((a, b) => a.rank - b.rank);
            this.challengeRankings = rankings;
          }
        );
    }
  }

  refreshChallenges() {
    this.challengeService
      .getChallengeCurrent()
      .subscribe(
        (c: Challenge) => {
          this.refreshRankings();
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
          this.c_current = c;
        }
      );
  }

}
