import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnChanges, OnInit } from '@angular/core';
import { Config } from 'src/app/interfaces/config';
import { ConfigService } from 'src/app/services/config.service';
import { ErrorHandlerService } from 'src/app/services/error-handler.service';

@Component({
  selector: 'app-config-s3',
  templateUrl: './config-s3.component.html',
  styleUrls: ['./config-s3.component.scss']
})
export class ConfigS3Component implements OnInit, OnChanges {
  host: string = "";
  port: number = 0;
  access_key: string = "";
  access_secret: string = "";
  buckets: { [key: string]: string } = {
    'bucket_replays': '',
    'bucket_thumbnails': '',
    'bucket_challenges': '',
    'bucket_matchsettings': ''
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
      .getConfig('s3')
      .subscribe({
        next: (config: Config) => {
          this.host = config['content']['host'];
          this.port = config['content']['port'];
          this.access_key = config['content']['access_key'];
          this.access_secret = config['content']['access_secret'];
          for (const key in config['content']) {
            if (key.startsWith('bucket_')) this.buckets[key] = config['content'][key];
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
      'port': this.port,
      'access_key': this.access_key,
      'access_secret': this.access_secret
    }
    for (let b in this.buckets) {
      content[b] = this.buckets[b]
    }
    this.configService
      .updateConfig('s3', content)
      .subscribe({
        error: (err: HttpErrorResponse) => {
          this.errorHandler.handleError(err);
        }
      })
  }

  bucketDisplay(name: string): string {
    return name.replace('bucket_', '').replace('_', ' ')
  }

}
