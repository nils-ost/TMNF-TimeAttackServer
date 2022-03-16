import { Component, OnInit } from '@angular/core';
import { ChallengeService } from '../../services/challenge.service';
import { RankingService } from '../../services/ranking.service';
import { PlayerService } from '../../services/player.service';
import { Challenge } from '../../interfaces/challenge';
import { ChallengeRanking } from '../../interfaces/ranking';
import { PlayerChallengeLaptime } from '../../interfaces/laptime';
import { Player } from '../../interfaces/player';

@Component({
  selector: 'app-challenges',
  templateUrl: './challenges.component.html',
  styleUrls: ['./challenges.component.scss']
})
export class ChallengesComponent implements OnInit {
  challenges: Challenge[] = [];
  currentChallenge?: Challenge;
  selectedChallenge?: Challenge;
  selectedChallengeRanking?: ChallengeRanking;
  challengeRankings: ChallengeRanking[] = [];
  playerChallengeLaptimes: PlayerChallengeLaptime[] = [];
  players: Player[] = [];

  constructor(
    private challengeService: ChallengeService,
    private rankingService: RankingService,
    private playerService: PlayerService
  ) { }

  ngOnInit(): void {
    this.refreshChallenges();
    this.refreshPlayers();
  }

  selectChallenge(event: any) {
    this.selectedChallengeRanking = undefined;
    this.playerChallengeLaptimes = [];
    if (event) {
      this.selectedChallenge = event.data
      this.rankingService
        .getChallengeRankings(event.data.id)
        .subscribe(
          (rankings: ChallengeRanking[]) => {
            this.challengeRankings = rankings;
          }
        );
    }
    else {
      this.selectedChallenge = undefined;
      this.challengeRankings = [];
    }
  }

  selectChallengeRanking(event: any) {
    if (event) {
      this.selectedChallengeRanking = event.data;
      if (this.selectedChallenge) {
        this.playerService
          .getPlayerChallengeLaptimes(event.data.player_id, this.selectedChallenge.id)
          .subscribe(
            (laptimes: PlayerChallengeLaptime[]) => {
              this.playerChallengeLaptimes = laptimes;
            }
          );
      }
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
      .getChallengeCurrent()
      .subscribe(
        (c: Challenge) => {
          this.currentChallenge = c;
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

}
