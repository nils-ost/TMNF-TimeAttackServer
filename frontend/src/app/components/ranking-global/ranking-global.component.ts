import { Component, OnInit } from '@angular/core';
import { GlobalRanking } from '../../interfaces/ranking';
import { Player } from '../../interfaces/player';
import { RankingService } from '../../services/ranking.service';
import { PlayerService } from '../../services/player.service';
import { timer } from 'rxjs';

@Component({
  selector: 'app-ranking-global',
  templateUrl: './ranking-global.component.html',
  styleUrls: ['./ranking-global.component.css']
})
export class RankingGlobalComponent implements OnInit {
  private refreshTimer = timer(10000, 10000);
  private refreshTimerSubscription = this.refreshTimer.subscribe(() => this.refreshData());

  globalRankings: GlobalRanking[] = [];
  players: Player[] = [];

  constructor(
    private rankingService: RankingService,
    private playerService: PlayerService
  ) { }

  ngOnInit(): void {
    this.refreshData();
  }

  refreshData() {
    this.playerService
      .getPlayers()
      .subscribe(
        (players: Player[]) => {
          this.players = players;
        }
      );
    this.rankingService
      .getGlobalRankings()
      .subscribe(
        (rankings: GlobalRanking[]) => {
          this.globalRankings = rankings;
        }
      );
  }

  public playerName(player_id: string): string {
    let p = this.players.find(p => p.id === player_id);
    if (p) return p.name;
    else return '--unknown--';
  }

}
