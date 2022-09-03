import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription, timer } from 'rxjs';
import { Router } from "@angular/router"
import { Settings } from '../../interfaces/settings';
import { SettingsService } from '../../services/settings.service';

@Component({
  selector: 'app-start-countdown',
  templateUrl: './start-countdown.component.html',
  styleUrls: ['./start-countdown.component.scss']
})
export class StartCountdownComponent implements OnInit, OnDestroy {
  refreshSettingsTimer = timer(60000, 60000);
  decrementCountdownTimer = timer(1000, 1000);
  refreshSettingsTimerSubscription: Subscription | undefined;
  decrementCountdownTimerSubscription: Subscription | undefined;
  settings?: Settings;
  countdown?: number;
  countdown_h: number | string = 99;
  countdown_m: number | string = 99;
  countdown_s: number | string = 99;

  constructor(
    private router: Router,
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
        this.router.navigate(['/wallboard']);
      }
      this.countdown_s = Math.floor((this.countdown) % 60);
      this.countdown_m = Math.floor((this.countdown / 60) % 60),
      this.countdown_h = Math.floor((this.countdown / (60 * 60)) % 24);
      this.countdown_s = this.countdown_s < 10 ? '0' + this.countdown_s : this.countdown_s;
      this.countdown_m = this.countdown_m < 10 ? '0' + this.countdown_m : this.countdown_m;
      this.countdown_h = this.countdown_h < 10 ? '0' + this.countdown_h : this.countdown_h;
    }
  }

  refreshSettings() {
    this.settingsService
      .getSettings()
      .subscribe(
        (s: Settings) => {
          this.settings = s;
          if (s.start_time) {
            this.countdown = (s.start_time + 5) - Math.floor(Date.now()/1000);
            if (this.countdown <= 0) {
              this.router.navigate(['/wallboard']);
            }
          }
          else {
            this.router.navigate(['/wallboard']);
          }
        }
      );
  }

}
