import { Component, OnInit } from '@angular/core';
import { PlayerRanking } from '../../interfaces/ranking';
import { Player } from '../../interfaces/player';
import { PlayerService } from '../../services/player.service';

@Component({
  selector: 'app-players',
  templateUrl: './players.component.html',
  styleUrls: ['./players.component.scss']
})
export class PlayersComponent implements OnInit {
  players: Player[] = [];
  selectedPlayer?: Player;
  playerRankings: PlayerRanking[] = [];

  constructor(
    private playerService: PlayerService
  ) { }

  ngOnInit(): void {
    this.refreshPlayers();
  }

  selectPlayer(event: any) {
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
