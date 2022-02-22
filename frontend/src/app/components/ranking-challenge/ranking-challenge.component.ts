import { Component, Input, OnInit } from '@angular/core';
import { ChallengeRanking } from '../../interfaces/ranking';
import { Player } from '../../interfaces/player';

@Component({
  selector: 'app-ranking-challenge',
  templateUrl: './ranking-challenge.component.html',
  styleUrls: ['./ranking-challenge.component.css']
})
export class RankingChallengeComponent implements OnInit {
  @Input() challengeRankings!: ChallengeRanking[];
  @Input() players!: Player[];

  constructor() { }

  ngOnInit(): void {
  }

  playerName(player_id: string): string {
    let p = this.players.find(p => p.id === player_id);
    if (p) return p.name;
    else return '--new player--';
  }

}
