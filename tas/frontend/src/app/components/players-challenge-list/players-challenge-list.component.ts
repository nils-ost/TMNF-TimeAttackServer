import { Component, Input, OnInit } from '@angular/core';
import { PlayerRanking } from '../../interfaces/ranking';

@Component({
  selector: 'app-players-challenge-list',
  templateUrl: './players-challenge-list.component.html',
  styleUrls: ['./players-challenge-list.component.scss']
})
export class PlayersChallengeListComponent implements OnInit {
  @Input() playerRankings!: PlayerRanking[];

  constructor() { }

  ngOnInit(): void {
  }

}
