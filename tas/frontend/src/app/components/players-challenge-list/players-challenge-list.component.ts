import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { PlayerRanking } from '../../interfaces/ranking';

@Component({
  selector: 'app-players-challenge-list',
  templateUrl: './players-challenge-list.component.html',
  styleUrls: ['./players-challenge-list.component.scss']
})
export class PlayersChallengeListComponent implements OnInit {
  @Input() playerRankings!: PlayerRanking[];
  @Output() selectPlayerRankingEvent = new EventEmitter<PlayerRanking | null>();
  selectedPlayerRanking?: PlayerRanking;

  constructor() { }

  ngOnInit(): void {
  }

  selectPlayerRanking(pr: PlayerRanking | null) {
    this.selectPlayerRankingEvent.emit(pr);
  }

}
