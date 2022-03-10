import { Component, OnInit } from '@angular/core';
import { Player } from '../../interfaces/player';
import { PlayerService } from '../../services/player.service';

@Component({
  selector: 'app-players',
  templateUrl: './players.component.html',
  styleUrls: ['./players.component.scss']
})
export class PlayersComponent implements OnInit {
  players: Player[] = [];

  constructor(
    private playerService: PlayerService
  ) { }

  ngOnInit(): void {
    this.refreshPlayers();
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
