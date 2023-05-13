import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Settings } from 'src/app/interfaces/settings';
import { SettingsService } from 'src/app/services/settings.service';

@Component({
  selector: 'app-hotseat-wallboard-screen',
  templateUrl: './hotseat-wallboard-screen.component.html',
  styleUrls: ['./hotseat-wallboard-screen.component.scss']
})
export class HotseatWallboardScreenComponent implements OnInit {
  settings?: Settings;

  constructor(
    private settingsService: SettingsService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.refreshSettings();
  }

  refreshSettings() {
    this.settingsService
      .getSettings()
      .subscribe(
        (settings: Settings) => {
          this.settings = settings;
          if (!settings.hotseat_mode) this.router.navigate(['/wallboard']);
        }
      );
  }

}
