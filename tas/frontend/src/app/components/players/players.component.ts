import { Component, OnInit } from '@angular/core';
import { PlayerRanking, GlobalRanking } from '../../interfaces/ranking';
import { Player } from '../../interfaces/player';
import { Challenge } from '../../interfaces/challenge';
import { PlayerService } from '../../services/player.service';
import { RankingService } from '../../services/ranking.service';
import { ChallengeService } from '../../services/challenge.service';
import { PlayerChallengeLaptime } from '../../interfaces/laptime';

@Component({
  selector: 'app-players',
  templateUrl: './players.component.html',
  styleUrls: ['./players.component.scss']
})
export class PlayersComponent implements OnInit {
  players: Player[] = [];
  globalRankings: GlobalRanking[] = [];
  selectedPlayer?: Player;
  playerRankings: PlayerRanking[] = [];
  challenges: Challenge[] = [];
  selectedPlayerRanking?: PlayerRanking;
  playerChallengeLaptimes: PlayerChallengeLaptime[] = [];

  constructor(
    private playerService: PlayerService,
    private rankingService: RankingService,
    private challengeService: ChallengeService
  ) { }

  ngOnInit(): void {
    this.refreshChallenges();
    this.refreshGlobalRanking();
    this.refreshPlayers();
  }

  selectPlayer(event: any) {
    this.selectedPlayerRanking = undefined;
    this.playerChallengeLaptimes = [];
    if (event) {
      this.selectedPlayer = event.data;
      this.playerService
        .getPlayerRankings(event.data.id)
        .subscribe(
          (pr: PlayerRanking[]) => {
            this.playerRankings = pr;
          }
        );
    }
    else {
      this.selectedPlayer = undefined;
      this.playerRankings = [];
    }
  }

  selectPlayerRanking(event: any) {
    if (event) {
      this.selectedPlayerRanking = event.data;
      if (this.selectedPlayer) {
        this.playerService
          .getPlayerChallengeLaptimes(this.selectedPlayer.id, event.data.challenge_id)
          .subscribe(
            (laptimes: PlayerChallengeLaptime[]) => {
              this.playerChallengeLaptimes = laptimes;
            }
          );
      }
    }
    else {
      this.selectedPlayerRanking = undefined;
      this.playerChallengeLaptimes = [];
    }
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

  refreshGlobalRanking() {
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
  }

}
