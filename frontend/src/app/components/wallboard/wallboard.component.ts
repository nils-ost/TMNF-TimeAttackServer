import { Component, OnInit } from '@angular/core';
import { Player } from '../../interfaces/player';
import { GlobalRanking } from '../../interfaces/ranking';
import { PlayerService } from '../../services/player.service';
import { RankingService } from '../../services/ranking.service';
import { Subscription, timer } from 'rxjs';

@Component({
  selector: 'app-wallboard',
  templateUrl: './wallboard.component.html',
  styleUrls: ['./wallboard.component.css']
})
export class WallboardComponent implements OnInit {
  refreshPlayersTimer = timer(30000, 30000);
  refreshRankingsTimer = timer(10000, 10000);
  refreshPlayersTimerSubscription: Subscription | undefined;
  refreshRankingsTimerSubscription: Subscription | undefined;

  players: Player[] = [];
  globalRankings: GlobalRanking[] = [];

  constructor(
    private playerService: PlayerService,
    private rankingService: RankingService
  ) { }

  ngOnInit(): void {
    this.refreshPlayers();
    this.enableAutoRefresh();
  }

  enableAutoRefresh() {
    this.refreshPlayersTimerSubscription = this.refreshPlayersTimer.subscribe(() => this.refreshPlayers());
    this.refreshRankingsTimerSubscription = this.refreshRankingsTimer.subscribe(() => this.refreshRankings());
  }

  disableAutoRefresh() {
    this.refreshPlayersTimerSubscription?.unsubscribe();
    this.refreshRankingsTimerSubscription?.unsubscribe();
  }

  refreshPlayers() {
    this.playerService
      .getPlayers()
      .subscribe(
        (players: Player[]) => {
          this.players = players;
        }
      );
  }

  refreshRankings() {
    this.rankingService
      .getGlobalRankings()
      .subscribe(
        (rankings: GlobalRanking[]) => {
          this.globalRankings = rankings;
        }
      );
  }

}
