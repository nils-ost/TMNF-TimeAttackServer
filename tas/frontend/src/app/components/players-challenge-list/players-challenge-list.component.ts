import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { PlayerRanking } from '../../interfaces/ranking';
import { Challenge } from '../../interfaces/challenge';
import { environment } from '../../../environments/environment';

interface SortablePlayerRanking {
    challenge_id: string;
    challenge_name: string;
    time: number;
    rank: number;
    points: number;
    at: number;
}

@Component({
  selector: 'app-players-challenge-list',
  templateUrl: './players-challenge-list.component.html',
  styleUrls: ['./players-challenge-list.component.scss']
})
export class PlayersChallengeListComponent implements OnInit, OnChanges {
  @Input() playerRankings!: PlayerRanking[];
  @Input() challenges!: Challenge[];
  @Input() thumbnails: boolean = false;
  @Output() selectPlayerRankingEvent = new EventEmitter<PlayerRanking | null>();
  selectedPlayerRanking?: PlayerRanking;
  sortablePlayerRankings: SortablePlayerRanking[] = [];
  thumbnailUrlBase: string = "";

  constructor() { }

  ngOnInit(): void {
    this.thumbnailUrlBase = environment.apiUrl + '/thumbnails/';
    this.buildSortablePlayerRankings();
  }

  ngOnChanges(changes: SimpleChanges) {
    this.buildSortablePlayerRankings();
  }

  selectPlayerRanking(pr: PlayerRanking | null) {
    this.selectPlayerRankingEvent.emit(pr);
  }

  buildSortablePlayerRankings() {
    let new_pr: SortablePlayerRanking[] = [];
    for (let i = 0; i < this.playerRankings.length; i++) {
      let spr: SortablePlayerRanking = {
        challenge_id: this.playerRankings[i].challenge_id,
        challenge_name: this.challengeName(this.playerRankings[i].challenge_id),
        time: this.playerRankings[i].time,
        rank: this.playerRankings[i].rank,
        points: this.playerRankings[i].points,
        at: this.playerRankings[i].at
      } as SortablePlayerRanking;
      new_pr.push(spr);
    }
    this.sortablePlayerRankings = new_pr;
  }

  challengeName(challenge_id: string): string {
    let c = this.challenges.find(c => c.id === challenge_id);
    if (c) return c.name;
    else return "--unknown--";
  }

}
