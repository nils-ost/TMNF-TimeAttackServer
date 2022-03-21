import { Component, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { GlobalRanking } from '../../interfaces/ranking';
import { Player } from '../../interfaces/player';

interface RankingDisplay {
    player_id: string;
    player_name: string;
    points: number;
    points_diff?: number;
    rank: number;
}

@Component({
  selector: 'app-playerhud-global-list',
  templateUrl: './playerhud-global-list.component.html',
  styleUrls: ['./playerhud-global-list.component.scss']
})
export class PlayerhudGlobalListComponent implements OnInit {
  @Input() globalRankings!: GlobalRanking[];
  @Input() players!: Player[];
  @Input() selectedPlayer!: Player;
  rankingDisplay: RankingDisplay[] = [];

  constructor() { }

  ngOnInit(): void {
    this.buildRankingDisplay();
  }

  ngOnChanges(changes: SimpleChanges) {
    this.buildRankingDisplay();
  }

  buildRankingDisplay() {
    let grs: GlobalRanking[] = [];
    let selectedGR: GlobalRanking | null = this.getGlobalRankingByPlayer(this.selectedPlayer.id);
    if (selectedGR) {
      grs.push(selectedGR);
      if (selectedGR.rank >= 4) {
        let gr: GlobalRanking | null = this.getGlobalRankingByRank(1);
        if (gr) grs.push(gr);
      }
      for (let i = selectedGR.rank - 1; i > selectedGR.rank - 3; i--) {
        let gr: GlobalRanking | null = this.getGlobalRankingByRank(i);
        if (gr) grs.push(gr);
      }
      for (let i = selectedGR.rank + 1; i < selectedGR.rank + 3; i++) {
        let gr: GlobalRanking | null = this.getGlobalRankingByRank(i);
        if (gr) grs.push(gr);
      }
    }
    else {
      for(let i = 1; i < 4; i++) {
        let gr: GlobalRanking | null = this.getGlobalRankingByRank(i);
        if (gr) grs.push(gr);
      }
    }

    let rds: RankingDisplay[] = [];
    for (let i = 0; i < grs.length; i++) {
      let gr: GlobalRanking = grs[i];
      let rd: RankingDisplay = {
        player_id: gr.player_id,
        player_name: this.getPlayerName(gr.player_id),
        points: gr.points,
        rank: gr.rank
      } as RankingDisplay;
      if (selectedGR) {
        rd.points_diff = selectedGR.points - rd.points;
      }
      rds.push(rd);
    }
    this.rankingDisplay = rds;
  }

  getGlobalRankingByRank(rank: number): GlobalRanking | null {
    let gr = this.globalRankings.find(gr => gr.rank === rank);
    if (gr) return gr;
    else return null;
  }

  getGlobalRankingByPlayer(player_id: string): GlobalRanking | null {
    let gr = this.globalRankings.find(gr => gr.player_id === player_id);
    if (gr) return gr;
    else return null;
  }

  getPlayerName(player_id: string): string {
    let p = this.players.find(p => p.id === player_id);
    if (p) return p.name;
    else return "--unknown--";
  }

}
