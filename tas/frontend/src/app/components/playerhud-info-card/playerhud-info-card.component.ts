import { Component, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { PlayerRanking } from '../../interfaces/ranking';
import { Challenge } from '../../interfaces/challenge';

@Component({
  selector: 'app-playerhud-info-card',
  templateUrl: './playerhud-info-card.component.html',
  styleUrls: ['./playerhud-info-card.component.scss']
})
export class PlayerhudInfoCardComponent implements OnInit, OnChanges {
  @Input() playerRankings!: PlayerRanking[];
  @Input() challenges!: Challenge[];
  bestChallengesNames: string[] = [];
  worstChallengesNames: string[] = [];
  missingChallengesNames: string[] = [];

  constructor() { }

  ngOnInit(): void {
    this.buildBestWorstChallenges();
    this.buildMissingChallenges();
  }

  ngOnChanges(changes: SimpleChanges) {
    this.buildBestWorstChallenges();
    this.buildMissingChallenges();
  }

  buildBestWorstChallenges() {
    let best: number = 9999;
    let worst: number = 0;
    let bestS: string[] = [];
    let worstS: string[] = [];
    for (let i = 0; i < this.playerRankings.length; i++) {
      let pr: PlayerRanking = this.playerRankings[i];
      if (pr.rank > worst) {
        worst = pr.rank;
        worstS = [];
      }
      if (pr.rank === worst) worstS.push(this.getChallengeNameById(pr.challenge_id));
      if (pr.rank < best) {
        best = pr.rank;
        bestS = [];
      }
      if (pr.rank === best) bestS.push(this.getChallengeNameById(pr.challenge_id));
    }
    this.bestChallengesNames = bestS;
    this.worstChallengesNames = worstS;
  }

  buildMissingChallenges() {
    let missingS: string[] = [];
    for (let i = 0; i < this.challenges.length; i++) {
      let c: Challenge = this.challenges[i];
      let pr = this.playerRankings.find(pr => pr.challenge_id === c.id);
      if (!pr) missingS.push(c.name);
    }
    this.missingChallengesNames = missingS;
  }

  getChallengeNameById(challenge_id: string): string {
    let c = this.challenges.find(c => c.id === challenge_id);
    if (c) return c.name;
    else return "--unknown--";
  }

}
