import { Component, Input, OnInit } from '@angular/core';
import { ChallengeRanking } from '../../interfaces/ranking';
import { Player } from '../../interfaces/player';
import { Challenge } from '../../interfaces/challenge';

@Component({
  selector: 'app-ranking-challenge',
  templateUrl: './ranking-challenge.component.html',
  styleUrls: ['./ranking-challenge.component.scss']
})
export class RankingChallengeComponent implements OnInit {
  @Input() challengeRankings!: ChallengeRanking[];
  @Input() players!: Player[];
  @Input() currentChallenge?: Challenge;
  @Input() nextChallenge?: Challenge;

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
