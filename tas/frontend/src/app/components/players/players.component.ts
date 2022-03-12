import { Component, OnInit } from '@angular/core';
import { PlayerRanking } from '../../interfaces/ranking';
import { Player } from '../../interfaces/player';
import { PlayerService } from '../../services/player.service';
import { PlayerChallengeLaptime } from '../../interfaces/laptime';

@Component({
  selector: 'app-players',
  templateUrl: './players.component.html',
  styleUrls: ['./players.component.scss']
})
export class PlayersComponent implements OnInit {
  players: Player[] = [];
  selectedPlayer?: Player;
  playerRankings: PlayerRanking[] = [];
  selectedPlayerRanking?: PlayerRanking;
  playerChallengeLaptimes: PlayerChallengeLaptime[] = [];

  constructor(
    private playerService: PlayerService
  ) { }

  ngOnInit(): void {
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

}
