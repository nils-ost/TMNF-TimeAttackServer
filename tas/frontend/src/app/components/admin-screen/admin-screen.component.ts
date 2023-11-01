import { Component, OnInit } from '@angular/core';
import { Config } from 'src/app/interfaces/config';
import { ConfigService } from 'src/app/services/config.service';
import { ErrorHandlerService } from 'src/app/services/error-handler.service';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'app-admin-screen',
  templateUrl: './admin-screen.component.html',
  styleUrls: ['./admin-screen.component.scss']
})
export class AdminScreenComponent implements OnInit {
  configs: Config[] = [];

  constructor(
    private errorHandler: ErrorHandlerService,
    private configService: ConfigService
  ) { }

  ngOnInit(): void {
    this.refreshConfigs();
  }

  refreshConfigs() {
    this.configService
      .getConfigs()
      .subscribe({
        next: (configs: Config[]) => {
          this.configs = configs;
        },
        error: (err: HttpErrorResponse) => {
          this.errorHandler.handleError(err);
        }
      })
  }

}
