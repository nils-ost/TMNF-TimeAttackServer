import { Component, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { ChallengeRanking } from '../../interfaces/ranking';
import { Player } from '../../interfaces/player';

interface RankingDisplay {
    player_id: string;
    player_name: string;
    time: number;
    time_diff?: number;
    rank: number;
}

@Component({
  selector: 'app-playerhud-current-list',
  templateUrl: './playerhud-current-list.component.html',
  styleUrls: ['./playerhud-current-list.component.scss']
})
export class PlayerhudCurrentListComponent implements OnInit, OnChanges {
  @Input() challengeRankings!: ChallengeRanking[];
  @Input() players!: Player[];
  @Input() selectedPlayer!: Player;
  @Input() additionalTop: number = 2;
  @Input() additionalBottom: number = 2;
  rankingDisplay: RankingDisplay[] = [];

  constructor() { }

  ngOnInit(): void {
    this.buildRankingDisplay();
  }

  ngOnChanges(changes: SimpleChanges) {
    this.buildRankingDisplay();
  }

  buildRankingDisplay() {
    let crs: ChallengeRanking[] = [];
    let selectedCR: ChallengeRanking | null = this.getChallengeRankingByPlayer(this.selectedPlayer.id);
    if (selectedCR) {
      crs.push(selectedCR);
      if (selectedCR.rank >= (this.additionalTop + 2)) {
        let cr: ChallengeRanking | null = this.getChallengeRankingByRank(1);
        if (cr) crs.push(cr);
      }
      for (let i = selectedCR.rank - 1; i > selectedCR.rank - (this.additionalTop + 1); i--) {
        let cr: ChallengeRanking | null = this.getChallengeRankingByRank(i);
        if (cr) crs.push(cr);
      }
      for (let i = selectedCR.rank + 1; i < selectedCR.rank + (this.additionalBottom + 1); i++) {
        let cr: ChallengeRanking | null = this.getChallengeRankingByRank(i);
        if (cr) crs.push(cr);
      }
    }
    else {
      for(let i = 1; i < (this.additionalTop + 2); i++) {
        let cr: ChallengeRanking | null = this.getChallengeRankingByRank(i);
        if (cr) crs.push(cr);
      }
    }

    let rds: RankingDisplay[] = [];
    for (let i = 0; i < crs.length; i++) {
      let cr: ChallengeRanking = crs[i];
      let rd: RankingDisplay = {
        player_id: cr.player_id,
        player_name: this.getPlayerName(cr.player_id),
        time: cr.time,
        rank: cr.rank
      } as RankingDisplay;
      if (selectedCR && selectedCR.time > 0) {
        rd.time_diff = rd.time - selectedCR.time;
      }
      rds.push(rd);
    }
    this.rankingDisplay = rds;
  }

  getChallengeRankingByRank(rank: number): ChallengeRanking | null {
    let cr = this.challengeRankings.find(cr => cr.rank === rank);
    if (cr) return cr
    else return null;
  }

  getChallengeRankingByPlayer(player_id: string): ChallengeRanking | null {
    let cr = this.challengeRankings.find(cr => cr.player_id === player_id);
    if (cr) return cr;
    else return null;
  }

  getPlayerName(player_id: string): string {
    let p = this.players.find(p => p.id === player_id);
    if (p) return p.name;
    else return "--unknown--";
  }

}
