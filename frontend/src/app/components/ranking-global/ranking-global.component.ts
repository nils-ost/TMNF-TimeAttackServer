import { Component, OnInit } from '@angular/core';
import { RankingGlobal } from '../../interfaces/ranking-global';
import { RankingGlobalService } from '../../services/ranking-global.service';

@Component({
  selector: 'app-ranking-global',
  templateUrl: './ranking-global.component.html',
  styleUrls: ['./ranking-global.component.css']
})
export class RankingGlobalComponent implements OnInit {

  rankingGlobals: RankingGlobal[] = [];

  constructor(
    private rankingGlobalService: RankingGlobalService
  ) { }

  ngOnInit(): void {
    this.rankingGlobalService
      .getRankingGlobal()
      .subscribe(
        (rankings: RankingGlobal[]) => {
          console.log(rankings);
          this.rankingGlobals = rankings;
        }
      );
  }

}
