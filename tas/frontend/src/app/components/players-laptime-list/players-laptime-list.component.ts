import { Component, Input, OnInit } from '@angular/core';
import { PlayerChallengeLaptime } from '../../interfaces/laptime';

@Component({
  selector: 'app-players-laptime-list',
  templateUrl: './players-laptime-list.component.html',
  styleUrls: ['./players-laptime-list.component.scss']
})
export class PlayersLaptimeListComponent implements OnInit {
  @Input() playerChallengeLaptimes!: PlayerChallengeLaptime[];
  @Input() bestLaptimeAt?: number;

  constructor() { }

  ngOnInit(): void {
  }

}
