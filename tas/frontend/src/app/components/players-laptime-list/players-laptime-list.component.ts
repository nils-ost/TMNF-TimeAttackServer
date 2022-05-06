import { Component, Input, OnInit } from '@angular/core';
import { PlayerChallengeLaptime } from '../../interfaces/laptime';
import { Settings } from '../../interfaces/settings';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-players-laptime-list',
  templateUrl: './players-laptime-list.component.html',
  styleUrls: ['./players-laptime-list.component.scss']
})
export class PlayersLaptimeListComponent implements OnInit {
  @Input() playerChallengeLaptimes!: PlayerChallengeLaptime[];
  @Input() bestLaptimeAt?: number;
  @Input() provide_replays: boolean = false;
  apiUrl: string = "";

  constructor() { }

  ngOnInit(): void {
    this.apiUrl = environment.apiUrl;
  }

}
