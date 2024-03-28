import { Component, OnInit } from '@angular/core';
import { MenuItem } from 'primeng/api';
import { DialogService, DynamicDialogRef } from 'primeng/dynamicdialog';
import { Config } from 'src/app/interfaces/config';
import { ConfigService } from 'src/app/services/config.service';
import { ErrorHandlerService } from 'src/app/services/error-handler.service';
import { HttpErrorResponse } from '@angular/common/http';
import { ConfigRabbitComponent } from '../config-rabbit/config-rabbit.component';
import { ConfigS3Component } from '../config-s3/config-s3.component';
import { ConfigChallengesComponent } from '../config-challenges/config-challenges.component';
import { ConfigDedicatedComponent } from '../config-dedicated/config-dedicated.component';
import { ConfigLokiComponent } from '../config-loki/config-loki.component';

@Component({
  selector: 'app-admin-screen',
  templateUrl: './admin-screen.component.html',
  styleUrls: ['./admin-screen.component.scss'],
  providers: [DialogService]
})
export class AdminScreenComponent implements OnInit {
  dialogRef: DynamicDialogRef | undefined;
  dedicated_configs: { [key: string]: any } = {};
  dedicatedConfigsSelector: MenuItem[] = [];

  constructor(
    private errorHandler: ErrorHandlerService,
    private configService: ConfigService,
    private dialogService: DialogService
  ) { }

  ngOnInit(): void {
    this.loadConfig();
  }

  loadConfig() {
    this.configService
      .getConfig('dedicated')
      .subscribe({
        next: (config: Config) => {
          this.dedicated_configs = config['content'];
          this.buildDedicatedConfigsSelector();
        },
        error: (err: HttpErrorResponse) => {
          this.errorHandler.handleError(err);
        }
      })
  }

  showRabbitConfig() {
    this.dialogRef = this.dialogService.open(ConfigRabbitComponent, {header: 'RabbitMQ Config', modal: true});
  }

  showS3Config() {
    this.dialogRef = this.dialogService.open(ConfigS3Component, {header: 'S3 Config', modal: true});
  }

  showChallengesConfig() {
    this.dialogRef = this.dialogService.open(ConfigChallengesComponent, {header: 'Challenges Config', modal: true});
  }

  showLokiConfig() {
    this.dialogRef = this.dialogService.open(ConfigLokiComponent, {header: 'Loki Config', modal: true});
  }

  showNewDedicatedConfig() {
    this.dialogRef = this.dialogService.open(ConfigDedicatedComponent, {header: 'Dedicated Config', data: {}, modal: true});
    this.dialogRef.onClose.subscribe(() => {this.loadConfig();});
  }

  buildDedicatedConfigsSelector() {
    this.dedicatedConfigsSelector = [];
    for (let k in this.dedicated_configs) {
      let item = {
        label: k,
        command: () => {
          this.dialogRef = this.dialogService.open(ConfigDedicatedComponent, {header: 'Dedicated Config', data: {selected_config: k}, modal: true});
          this.dialogRef.onClose.subscribe(() => {this.loadConfig();});
        }
      }
      this.dedicatedConfigsSelector.push(item);
    }
  }

}
