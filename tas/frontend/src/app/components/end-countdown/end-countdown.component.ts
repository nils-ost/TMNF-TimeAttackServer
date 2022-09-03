import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription, timer } from 'rxjs';
import { Settings } from '../../interfaces/settings';
import { SettingsService } from '../../services/settings.service';

@Component({
  selector: 'app-end-countdown',
  templateUrl: './end-countdown.component.html',
  styleUrls: ['./end-countdown.component.scss']
})
export class EndCountdownComponent implements OnInit, OnDestroy {
  refreshSettingsTimer = timer(60000, 60000);
  decrementCountdownTimer = timer(1000, 1000);
  refreshSettingsTimerSubscription: Subscription | undefined;
  decrementCountdownTimerSubscription: Subscription | undefined;
  settings?: Settings;
  end_infinite: boolean = false;
  end_reached: boolean = false;
  countdown: number = 4000;
  countdown_h: number | string = 99;
  countdown_m: number | string = 99;
  countdown_s: number | string = 99;

  constructor(
    private settingsService: SettingsService
  ) { }

  ngOnInit(): void {
    this.refreshSettings();
    this.refreshSettingsTimerSubscription = this.refreshSettingsTimer.subscribe(() => this.refreshSettings());
    this.decrementCountdownTimerSubscription = this.decrementCountdownTimer.subscribe(() => this.decrementCountdown());
  }

  ngOnDestroy(): void {
    this.refreshSettingsTimerSubscription?.unsubscribe();
    this.decrementCountdownTimerSubscription?.unsubscribe();
  }

  decrementCountdown() {
    if (this.countdown) {
      this.countdown = this.countdown - 1;
      if (this.countdown <= 0) {
        this.end_reached = true;
        this.decrementCountdownTimerSubscription?.unsubscribe();
      }
      else {
        this.countdown_s = Math.floor((this.countdown) % 60);
        this.countdown_m = Math.floor((this.countdown / 60) % 60),
        this.countdown_h = Math.floor((this.countdown / (60 * 60)) % 24);
        this.countdown_s = this.countdown_s < 10 ? '0' + this.countdown_s : this.countdown_s;
        this.countdown_m = this.countdown_m < 10 ? '0' + this.countdown_m : this.countdown_m;
        this.countdown_h = this.countdown_h < 10 ? '0' + this.countdown_h : this.countdown_h;
      }
    }
  }

  refreshSettings() {
    this.settingsService
      .getSettings()
      .subscribe(
        (s: Settings) => {
          this.settings = s;
          if (s.end_time) {
            this.countdown = (s.end_time + 5) - Math.floor(Date.now()/1000);
            if (this.countdown <= 0) {
              this.end_reached = true;
            }
          }
          else {
            this.end_infinite = true;
          }
        }
      );
  }

}
