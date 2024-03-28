import { HttpErrorResponse } from '@angular/common/http';
import { Component, Input, OnChanges, OnInit } from '@angular/core';
import { DynamicDialogConfig, DynamicDialogRef } from 'primeng/dynamicdialog';
import { Config } from 'src/app/interfaces/config';
import { ConfigService } from 'src/app/services/config.service';
import { ErrorHandlerService } from 'src/app/services/error-handler.service';
import { MatchsettingService } from 'src/app/services/matchsetting.service';

@Component({
  selector: 'app-config-dedicated',
  templateUrl: './config-dedicated.component.html',
  styleUrls: ['./config-dedicated.component.scss']
})
export class ConfigDedicatedComponent implements OnInit, OnChanges {
  @Input() selected_config?: string;
  matchsettings: string[] = [];
  dedicated_configs: { [key: string]: any } = {};
  name_valid_characters: string = "abcdefghijklmnopqrstuvwxyz1234567890-_";
  // fields
  name: string = "";
  connection: string = "local-container";
  container: string = "tmnfd";
  type: string = "tmnf";
  active_matchsetting: string = 'NationsWhite.txt';
  game_port_auto: boolean = true;
  game_port: number = 0;
  p2p_port_auto: boolean = true;
  p2p_port: number = 0;
  rpc_port_auto: boolean = true;
  rpc_port: number = 0;
  superadmin_pw: string = "";
  admin_pw: string = "";
  user_pw: string = "";
  max_players: number = 0;
  ingame_name: string = "";
  callvote_timeout: number = 0;
  callvote_ratio: number = 0;
  // error markers
  name_error?: string;

  constructor(
    private errorHandler: ErrorHandlerService,
    private configService: ConfigService,
    private matchsettingsService: MatchsettingService,
    public dialogRef: DynamicDialogRef,
    public config: DynamicDialogConfig
  ) { }

  ngOnInit(): void {
    this.loadMatchsettings();
    this.loadConfig();
  }

  ngOnChanges(): void {
    this.loadMatchsettings();
    this.loadConfig();
  }

  loadMatchsettings() {
    this.matchsettingsService
      .getMatchsettings()
      .subscribe({
        next: (matchsettings: string[]) => {
          this.matchsettings = matchsettings;
        },
        error: (err: HttpErrorResponse) => {
          this.errorHandler.handleError(err);
        }
      })
  }

  loadConfig() {
    this.configService
      .getConfig('dedicated')
      .subscribe({
        next: (config: Config) => {
          this.dedicated_configs = config['content'];
          this.fillFields();
        },
        error: (err: HttpErrorResponse) => {
          this.errorHandler.handleError(err);
        }
      })
  }

  saveConfig() {
    if (this.validateName()) {
      let item: { [key: string]: any} = {};
      item['connection'] = this.connection;
      item['container'] = this.container;
      item['type'] = this.type;
      if (!this.game_port_auto)
        item['game_port'] = this.game_port
      if (!this.p2p_port_auto)
        item['p2p_port'] = this.p2p_port
      if (!this.rpc_port_auto)
        item['rpc_port'] = this.rpc_port
      item['superadmin_pw'] = this.superadmin_pw
      item['admin_pw'] = this.admin_pw
      item['user_pw'] = this.user_pw
      item['max_players'] = this.max_players
      item['ingame_name'] = this.ingame_name
      item['callvote_timeout'] = this.callvote_timeout
      item['callvote_ratio'] = this.callvote_ratio
      item['active_matchsetting'] = this.active_matchsetting
      if (this.selected_config && this.selected_config != this.name) {
        delete this.dedicated_configs[this.selected_config];
      }
      this.dedicated_configs[this.name] = item;
      this.configService
        .updateConfig('dedicated', this.dedicated_configs)
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

  dismissConfig() {
    this.dialogRef.close()
  }

  deleteConfig() {
    if (this.selected_config) {
      delete this.dedicated_configs[this.selected_config];
      this.configService
      .updateConfig('dedicated', this.dedicated_configs)
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

  fillFields() {
    if (this.config.data && this.config.data.selected_config)
      this.selected_config = this.config.data.selected_config
    else
      this.selected_config = undefined;
    this.name = "";
    this.connection = "local-container";
    this.container = "tmnfd";
    this.type = "tmnf";
    this.game_port_auto = true;
    this.game_port = 2350;
    this.p2p_port_auto = true;
    this.p2p_port = 3450;
    this.rpc_port_auto = true;
    this.rpc_port = 5000;
    this.superadmin_pw = "SuperAdmin";
    this.admin_pw = "Admin";
    this.user_pw = "User";
    this.max_players = 32;
    this.ingame_name = "TM-TAS";
    this.callvote_timeout = 0;
    this.callvote_ratio = -1;
    if (this.selected_config && this.selected_config in this.dedicated_configs) {
      this.name = this.selected_config;
      if ('connection' in this.dedicated_configs[this.selected_config])
        this.connection = this.dedicated_configs[this.selected_config]['connection'];
      if ('container' in this.dedicated_configs[this.selected_config])
        this.container = this.dedicated_configs[this.selected_config]['container'];
      if ('type' in this.dedicated_configs[this.selected_config])
        this.type = this.dedicated_configs[this.selected_config]['type'];
      if ('game_port' in this.dedicated_configs[this.selected_config]) {
        this.game_port = this.dedicated_configs[this.selected_config]['game_port']
        this.game_port_auto = false;
      }
      if ('p2p_port' in this.dedicated_configs[this.selected_config]) {
        this.p2p_port = this.dedicated_configs[this.selected_config]['p2p_port']
        this.p2p_port_auto = false;
      }
      if ('rpc_port' in this.dedicated_configs[this.selected_config]) {
        this.rpc_port = this.dedicated_configs[this.selected_config]['rpc_port']
        this.rpc_port_auto = false;
      }
      if ('superadmin_pw' in this.dedicated_configs[this.selected_config])
        this.superadmin_pw = this.dedicated_configs[this.selected_config]['superadmin_pw']
      if ('admin_pw' in this.dedicated_configs[this.selected_config])
        this.admin_pw = this.dedicated_configs[this.selected_config]['admin_pw']
      if ('user_pw' in this.dedicated_configs[this.selected_config])
        this.user_pw = this.dedicated_configs[this.selected_config]['user_pw']
      if ('max_players' in this.dedicated_configs[this.selected_config])
        this.max_players = this.dedicated_configs[this.selected_config]['max_players']
      if ('ingame_name' in this.dedicated_configs[this.selected_config])
        this.ingame_name = this.dedicated_configs[this.selected_config]['ingame_name']
      if ('callvote_timeout' in this.dedicated_configs[this.selected_config])
        this.callvote_timeout = this.dedicated_configs[this.selected_config]['callvote_timeout']
      if ('callvote_ratio' in this.dedicated_configs[this.selected_config])
        this.callvote_ratio = this.dedicated_configs[this.selected_config]['callvote_ratio']
      if ('active_matchsetting' in this.dedicated_configs[this.selected_config])
        this.active_matchsetting = this.dedicated_configs[this.selected_config]['active_matchsetting']
    }
  }

  validateName(): boolean {
    if (!(this.selected_config && this.selected_config.toLowerCase() == this.name.toLowerCase())){
      for (let k in this.dedicated_configs) {
        if (this.name.toLowerCase() == k.toLowerCase()) {
          this.name_error = $localize `:@@DedicatedNameErrorAlreadyGiven:name is allready in use`;
          return false;
        }
      }
    }
    for (const k of this.name.toLowerCase()) {
      if (!this.name_valid_characters.includes(k)) {
        this.name_error = $localize `:@@DedicatedNameErrorInvalidCharacter:contains an invalid character`;
        return false;
      }
    }
    this.name_error = undefined;
    return true;
  }

}
