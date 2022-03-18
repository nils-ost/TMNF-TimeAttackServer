import { Component, OnInit } from '@angular/core';
import { Player } from '../../interfaces/player';
import { PlayerService } from '../../services/player.service';

@Component({
  selector: 'app-playerhud',
  templateUrl: './playerhud.component.html',
  styleUrls: ['./playerhud.component.scss']
})
export class PlayerhudComponent implements OnInit {
  players: Player[] = [];
  playerMe?: Player;
  selectedPlayerID?: string;

  constructor(
    private playerService: PlayerService
  ) { }

  ngOnInit(): void {
    this.getPlayerMe();
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

  getPlayerMe() {
    this.playerService
      .getPlayerMe()
      .subscribe(
        (player: Player | null) => {
          if (player) {
            this.playerMe = player;
          }
          else {
            this.refreshPlayers();
            this.playerMe = undefined;
          }
        }
      );
  }

  setPlayerMe(player_id: string) {
  }

}
