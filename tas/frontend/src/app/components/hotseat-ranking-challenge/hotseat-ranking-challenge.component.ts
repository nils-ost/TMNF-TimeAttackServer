import { Component, Input, OnChanges, OnInit } from '@angular/core';
import { Player } from 'src/app/interfaces/player';
import { ChallengeRanking } from 'src/app/interfaces/ranking';

@Component({
  selector: 'app-hotseat-ranking-challenge',
  templateUrl: './hotseat-ranking-challenge.component.html',
  styleUrls: ['./hotseat-ranking-challenge.component.scss']
})
export class HotseatRankingChallengeComponent implements OnInit, OnChanges {
  @Input() challengeRankings: ChallengeRanking[] = [];
  @Input() players: Player[] = [];
  @Input() pageNum: number = 1;
  @Input() pageSize: number = 10;
  rankingsDisplay: ChallengeRanking[] = [];

  constructor() { }

  ngOnInit(): void {
    this.refreshRankingsDisplay();
  }

  ngOnChanges(): void {
    this.refreshRankingsDisplay();
  }

  refreshRankingsDisplay() {
    let start: number = this.pageSize * (this.pageNum - 1);
    let end: number = Math.min(this.pageSize * this.pageNum, this.challengeRankings.length);
    let result: ChallengeRanking[] = [];
    for(let i = start; i < end; i++) {
      result.push(this.challengeRankings[i]);
    }
    this.rankingsDisplay = result;
  }

  playerName(player_id: string): string {
    let p = this.players.find(p => p.id === player_id);
    if (p) return p.name;
    else return '--new player--';
  }

  playerActive(player_id: string): boolean {
    let p = this.players.find(p => p.id === player_id);
    if (p) return (((Date.now() / 1000) - p.last_update) <= 60);
    else return false;
  }

}
