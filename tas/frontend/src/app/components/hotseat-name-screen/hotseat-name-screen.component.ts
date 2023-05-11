import { Component, OnDestroy, OnInit } from '@angular/core';
import { Player } from 'src/app/interfaces/player';
import { Settings } from 'src/app/interfaces/settings';
import { PlayerService } from 'src/app/services/player.service';
import { SettingsService } from 'src/app/services/settings.service';
import { Subscription, timer } from 'rxjs';

@Component({
  selector: 'app-hotseat-name-screen',
  templateUrl: './hotseat-name-screen.component.html',
  styleUrls: ['./hotseat-name-screen.component.scss']
})
export class HotseatNameScreenComponent implements OnInit, OnDestroy {
  refreshPlayerHotseatTimer = timer(5000, 5000);
  refreshPlayerHotseatTimerSubscription: Subscription | undefined;

  playerHotseat?: Player;
  settings?: Settings;
  newPlayerName: string = "";

  constructor(
    private playerService: PlayerService,
    private settingsService: SettingsService
  ) { }

  ngOnInit(): void {
    this.refreshSettings();
    this.refreshPlayerHotseat();
    this.enableAutoRefresh();
  }

  ngOnDestroy(): void {
    this.disableAutoRefresh();
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

  refreshPlayerHotseat() {
    this.playerService
      .getPlayerHotseat()
      .subscribe(
        (player: Player | null) => {
          if (player) {
            this.playerHotseat = player;
          }
          else {
            this.playerHotseat = undefined;
          }
        }
      );
  }

  enableAutoRefresh() {
    this.refreshPlayerHotseatTimerSubscription = this.refreshPlayerHotseatTimer.subscribe(() => this.refreshPlayerHotseat());
  }

  disableAutoRefresh() {
    this.refreshPlayerHotseatTimerSubscription?.unsubscribe();
  }

  sendPlayerHotseat() {
    if (this.newPlayerName != "") {
      this.playerService
        .setPlayerHotseat(this.newPlayerName)
        .subscribe(() => {
          this.refreshPlayerHotseat();
          this.newPlayerName = "";
        });
    }
  }

}
