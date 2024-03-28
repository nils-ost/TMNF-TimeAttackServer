import { Component, OnChanges, OnInit } from '@angular/core';
import { DynamicDialogRef } from 'primeng/dynamicdialog';
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
    private configService: ConfigService,
    public dialogRef: DynamicDialogRef
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
    let content: { [key: string]: any } = {
      'host': this.host,
      'port': this.port
    }
    for (let q in this.queues) {
      content[q] = this.queues[q]
    }
    this.configService
      .updateConfig('rabbit', content)
      .subscribe({
        next: () => {
          this.dialogRef.close();
        },
        error: (err: HttpErrorResponse) => {
          this.errorHandler.handleError(err);
        }
      })
  }

  queueDisplay(name: string): string {
    return name.replace('queue_', '').replace('_', ' ')
  }

}
