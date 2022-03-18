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
  filteredPlayers: Player[] = [];
  playerMe?: Player;
  selectedPlayerID?: string;

  constructor(
    private playerService: PlayerService
  ) { }

  ngOnInit(): void {
    this.refreshPlayerMe();
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
          }
          else {
            this.refreshPlayers();
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
}
