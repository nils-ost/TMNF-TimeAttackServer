import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnChanges, OnInit } from '@angular/core';
import { Config } from 'src/app/interfaces/config';
import { ConfigService } from 'src/app/services/config.service';
import { ErrorHandlerService } from 'src/app/services/error-handler.service';

@Component({
  selector: 'app-config-challenges',
  templateUrl: './config-challenges.component.html',
  styleUrls: ['./config-challenges.component.scss']
})
export class ConfigChallengesComponent implements OnInit, OnChanges {
  rel_time: string = "";
  least_rounds: number = 1;
  least_time: number = 30;

  constructor(
    private errorHandler: ErrorHandlerService,
    private configService: ConfigService
  ) { }

  ngOnChanges(): void {
    this.loadConfig();
  }

  ngOnInit(): void {
    this.loadConfig();
  }

  loadConfig() {
    this.configService
      .getConfig('challenges')
      .subscribe({
        next: (config: Config) => {
          this.rel_time = config['content']['rel_time'];
          this.least_rounds = config['content']['least_rounds'];
          this.least_time = config['content']['least_time'] / 1000;
        },
        error: (err: HttpErrorResponse) => {
          this.errorHandler.handleError(err);
        }
      })
  }

  saveConfig() {
    let content: { [key: string]: any } = {
      'rel_time': this.rel_time,
      'least_rounds': this.least_rounds,
      'least_time': this.least_time * 1000
    }
    this.configService
      .updateConfig('challenges', content)
      .subscribe({
        error: (err: HttpErrorResponse) => {
          this.errorHandler.handleError(err);
        }
      })
  }

}
