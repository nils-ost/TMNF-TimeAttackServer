import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { DynamicDialogRef } from 'primeng/dynamicdialog';
import { Config } from 'src/app/interfaces/config';
import { ConfigService } from 'src/app/services/config.service';
import { ErrorHandlerService } from 'src/app/services/error-handler.service';

@Component({
  selector: 'app-config-loki',
  templateUrl: './config-loki.component.html',
  styleUrls: ['./config-loki.component.scss']
})
export class ConfigLokiComponent implements OnInit {
  enable: boolean = true;
  host: string = "";
  port: number = 3100;
  protocol: string = "http";
  stream_prefix: string = "TAS - ";

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
      .getConfig('loki')
      .subscribe({
        next: (config: Config) => {
          this.enable = config['content']['enable'];
          this.host = config['content']['host'];
          this.port = config['content']['port'];
          this.protocol = config['content']['protocol'];
          this.stream_prefix = config['content']['stream_prefix'];
        },
        error: (err: HttpErrorResponse) => {
          this.errorHandler.handleError(err);
        }
      })
  }

  saveConfig() {
    let content: { [key: string]: any } = {
      'enable': this.enable,
      'host': this.host,
      'port': this.port,
      'protocol': this.protocol,
      'stream_prefix': this.stream_prefix
    }
    this.configService
      .updateConfig('loki', content)
      .subscribe({
        next: () => {
          this.dialogRef.close();
        },
        error: (err: HttpErrorResponse) => {
          this.errorHandler.handleError(err);
        }
      })
  }

}
