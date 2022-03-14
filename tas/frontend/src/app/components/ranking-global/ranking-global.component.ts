import { Component, Input, OnInit } from '@angular/core';
import { GlobalRanking } from '../../interfaces/ranking';
import { Player } from '../../interfaces/player';

@Component({
  selector: 'app-ranking-global',
  templateUrl: './ranking-global.component.html',
  styleUrls: ['./ranking-global.component.scss']
})
export class RankingGlobalComponent implements OnInit {
  @Input() globalRankings!: GlobalRanking[];
  @Input() players!: Player[];

  constructor() { }

  ngOnInit(): void {
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
