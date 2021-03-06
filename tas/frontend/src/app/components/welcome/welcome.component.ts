import { Component, OnInit } from '@angular/core';
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
export class WelcomeComponent implements OnInit {
  uri: String = window.location.pathname;
  settings?: Settings;
  stats?: Stats;
  laptimes_sum_h: number = 0;
  laptimes_sum_m: number = 0;
  laptimes_sum_s: number = 0;
  client_download_url?: string;

  constructor(
    private settingsService: SettingsService,
    private statsService: StatsService
  ) { }

  ngOnInit(): void {
    this.refreshSettings();
    this.refreshStats();
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

}
