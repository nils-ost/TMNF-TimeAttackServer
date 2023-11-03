import { Component, OnChanges, OnInit } from '@angular/core';
import { ConfigService } from 'src/app/services/config.service';
import { ErrorHandlerService } from 'src/app/services/error-handler.service';
import { HttpErrorResponse } from '@angular/common/http';
import { Config } from 'src/app/interfaces/config';

@Component({
  selector: 'app-config-rabbit',
  templateUrl: './config-rabbit.component.html',
  styleUrls: ['./config-rabbit.component.scss']
})
export class ConfigRabbitComponent implements OnInit, OnChanges {
  host: string = "";
  port: number = 0;
  queues: { [key: string]: string } = {
    'queue_dedicated_received_messages': '',
    'queue_dedicated_state_changes': '',
    'queue_orchestrator': ''
  }

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
      .getConfig('rabbit')
      .subscribe({
        next: (config: Config) => {
          this.host = config['content']['host'];
          this.port = config['content']['port'];
          for (const key in config['content']) {
            if (key.startsWith('queue_')) this.queues[key] = config['content'][key];
          }
        },
        error: (err: HttpErrorResponse) => {
          this.errorHandler.handleError(err);
        }
      })
  }

  saveConfig() {
    console.log(this.queues);
  }

  queueDisplay(name: string): string {
    return name.replace('queue_', '').replace('_', ' ')
  }

}
