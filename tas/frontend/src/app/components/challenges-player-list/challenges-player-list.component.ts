import { Component, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { ChallengeRanking } from '../../interfaces/ranking';
import { Player } from '../../interfaces/player';

interface SortableChallengeRanking {
  player_id: string;
  player_name: string;
  time: number;
  rank: number;
  points: number;
  at: number;
}

@Component({
  selector: 'app-challenges-player-list',
  templateUrl: './challenges-player-list.component.html',
  styleUrls: ['./challenges-player-list.component.scss']
})
export class ChallengesPlayerListComponent implements OnInit, OnChanges {
  @Input() challengeRankings!: ChallengeRanking[];
  @Input() players!: Player[];
  sortableChallengeRankings: SortableChallengeRanking[] = [];

  constructor() { }

  ngOnInit(): void {
    this.buildSortableChallengeRankings();
  }

  ngOnChanges(changes: SimpleChanges) {
    this.buildSortableChallengeRankings();
  }

  buildSortableChallengeRankings() {
    let scrl: SortableChallengeRanking[] = [];
    for (let i = 0; i < this.challengeRankings.length; i++) {
      let cr: ChallengeRanking = this.challengeRankings[i];
      let scr: SortableChallengeRanking = {
        player_id: cr.player_id,
        player_name: "",
        time: cr.time,
        rank: cr.rank,
        points: cr.points,
        at: cr.at
      } as SortableChallengeRanking;
    }
    this.sortableChallengeRankings = scrl;
  }

  playerName(player_id: string): string {
    let p = this.players.find(p => p.id === player_id);
    if (p) return p.name;
    else return "--unknown--";
  }

}
