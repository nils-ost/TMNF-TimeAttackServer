import { Component, OnInit } from '@angular/core';
import { Player } from '../../interfaces/player';
import { Settings } from '../../interfaces/settings';
import { PlayerService } from '../../services/player.service';
import { SettingsService } from '../../services/settings.service';

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
  settings?: Settings;

  constructor(
    private playerService: PlayerService,
    private settingsService: SettingsService
  ) { }

  ngOnInit(): void {
    this.refreshPlayerMe();
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
            this.refreshSettings();
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
