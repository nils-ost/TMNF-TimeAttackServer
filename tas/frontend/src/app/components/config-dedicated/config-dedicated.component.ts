import { HttpErrorResponse } from '@angular/common/http';
import { Component, Input, OnChanges, OnInit } from '@angular/core';
import { Config } from 'src/app/interfaces/config';
import { ConfigService } from 'src/app/services/config.service';
import { ErrorHandlerService } from 'src/app/services/error-handler.service';

@Component({
  selector: 'app-config-dedicated',
  templateUrl: './config-dedicated.component.html',
  styleUrls: ['./config-dedicated.component.css']
})
export class ConfigDedicatedComponent implements OnInit, OnChanges {
  @Input() selected_config: string | null = null;
  dedicated_configs: { [key: string]: any } = {};
  // fields
  name: string = "";
  connection: string = "";
  container: string = "";
  type: string = "";

  constructor(
    private errorHandler: ErrorHandlerService,
    private configService: ConfigService
  ) { }

  ngOnInit(): void {
    this.loadConfig();
  }

  ngOnChanges(): void {
    this.loadConfig();
  }

  loadConfig() {
    this.configService
      .getConfig('dedicated')
      .subscribe({
        next: (config: Config) => {
          this.dedicated_configs = config['content'];
        },
        error: (err: HttpErrorResponse) => {
          this.errorHandler.handleError(err);
        }
      })
  }

  saveConfig() {
  }

  fillFields() {
    this.name = "";
    this.connection = "";
    this.container = "";
    this.type = "";
    if (this.selected_config != null && this.selected_config in this.dedicated_configs) {
      this.name = this.selected_config;
      this.connection = this.dedicated_configs[this.selected_config]['connection'];
      this.container = this.dedicated_configs[this.selected_config]['container'];
      this.type = this.dedicated_configs[this.selected_config]['type'];
    }
  }

}
