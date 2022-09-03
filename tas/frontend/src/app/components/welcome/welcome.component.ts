import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription, timer } from 'rxjs';
import { Settings } from '../../interfaces/settings';
import { Stats } from '../../interfaces/stats';
import { SettingsService } from '../../services/settings.service';
import { StatsService } from '../../services/stats.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-welcome',
  templateUrl: './welcome.component.html',
  styleUrls: ['./welcome.component.scss']
})
export class WelcomeComponent implements OnInit, OnDestroy {
  refreshSettingsTimer = timer(60000, 60000);
  decrementCountdownTimer = timer(1000, 1000);
  refreshSettingsTimerSubscription: Subscription | undefined;
  decrementCountdownTimerSubscription: Subscription | undefined;
  uri: String = window.location.pathname;
  settings?: Settings;
  stats?: Stats;
  laptimes_sum_h: number = 0;
  laptimes_sum_m: number = 0;
  laptimes_sum_s: number = 0;
  client_download_url?: string;
  start_countdown: boolean = false;
  end_countdown: boolean = false;
  countdown?: number;
  countdown_h: number | string = 99;
  countdown_m: number | string = 99;
  countdown_s: number | string = 99;

  constructor(
    private settingsService: SettingsService,
    private statsService: StatsService
  ) { }

  ngOnInit(): void {
    this.refreshSettings();
    this.refreshStats();
    this.refreshSettingsTimerSubscription = this.refreshSettingsTimer.subscribe(() => this.refreshSettings());
    this.decrementCountdownTimerSubscription = this.decrementCountdownTimer.subscribe(() => this.decrementCountdown());
  }

  ngOnDestroy(): void {
    this.refreshSettingsTimerSubscription?.unsubscribe();
    this.decrementCountdownTimerSubscription?.unsubscribe();
  }

  refreshSettings() {
    this.settingsService
      .getSettings()
      .subscribe(
        (settings: Settings) => {
          this.settings = settings
          if (settings.client_download_url) {
            if (settings.client_download_url.startsWith('http')) this.client_download_url = settings.client_download_url;
            else this.client_download_url = environment.apiUrl + settings.client_download_url;
          }
          else this.client_download_url = undefined;
          if (settings.start_time) {
            let countdown: number = (settings.start_time + 5) - Math.floor(Date.now()/1000);
            if (countdown > 0) {
              this.countdown = countdown;
              this.start_countdown = true;
            }
            else {
              this.start_countdown = false;
            }
          }
          if (settings.end_time && !this.start_countdown) {
            let countdown: number = (settings.end_time + 5) - Math.floor(Date.now()/1000);
            if (countdown > 0) {
              this.countdown = countdown;
              this.end_countdown = true;
            }
            else {
              this.end_countdown = false;
            }
          }
        }
      );
  }

  refreshStats() {
    this.statsService
      .getStats()
      .subscribe(
        (stats: Stats) => {
          this.stats = stats
          let lts = Math.floor(stats.laptimes_sum / 1000);
          this.laptimes_sum_h = Math.floor(lts / 3600);
          lts = lts % 3600;
          this.laptimes_sum_m = Math.floor(lts / 60);
          this.laptimes_sum_s = lts % 60;
        }
      );
  }

  decrementCountdown() {
    if (this.countdown && (this.start_countdown || this.end_countdown)) {
      this.countdown = this.countdown - 1;
      if (this.countdown <= 0) {
        this.start_countdown = false;
        this.end_countdown = false;
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

}
