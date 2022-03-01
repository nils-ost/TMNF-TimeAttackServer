import { Component, OnInit, OnDestroy } from '@angular/core';
import { Player } from '../../interfaces/player';
import { GlobalRanking, ChallengeRanking } from '../../interfaces/ranking';
import { Challenge } from '../../interfaces/challenge';
import { PlayerService } from '../../services/player.service';
import { RankingService } from '../../services/ranking.service';
import { ChallengeService } from '../../services/challenge.service';
import { Subscription, timer, Subject } from 'rxjs';
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-wallboard',
  templateUrl: './wallboard.component.html',
  styleUrls: ['./wallboard.component.scss']
})
export class WallboardComponent implements OnInit {
  refreshPlayersTimer = timer(30000, 30000);
  refreshChallengesTimer = timer(10000, 10000);
  refreshPlayersTimerSubscription: Subscription | undefined;
  refreshChallengesTimerSubscription: Subscription | undefined;
  switchAutoRefreshSubscription: Subscription | undefined;

  players: Player[] = [];
  globalRankings: GlobalRanking[] = [];
  challengeRankings: ChallengeRanking[] = [];
  challenges: Challenge[] = [];
  c_current!: Challenge;
  c_next!: Challenge;
  switchAutoRefreshSubject: Subject<boolean> = new Subject<boolean>();

  speeddail_menu: MenuItem[] = [];

  constructor(
    private playerService: PlayerService,
    private rankingService: RankingService,
    private challengeService: ChallengeService
  ) { }

  ngOnInit(): void {
    this.refreshPlayers();
    this.refreshChallenges();
    this.enableAutoRefresh();

    this.switchAutoRefreshSubscription = this.switchAutoRefreshSubject.subscribe(
      (switchOn) => {
        if (switchOn) this.enableAutoRefresh();
        else this.disableAutoRefresh();
      }
    );

    this.speeddail_menu = [
        {
            tooltipOptions: {
                tooltipLabel: "Enable AutoRefresh",
                tooltipPosition: "top"
            },
            icon: 'pi pi-refresh',
            command: () => {
                this.switchAutoRefreshSubject.next(true);
            }
        },
        {
            tooltipOptions: {
                tooltipLabel: "Disable AutoRefresh",
                tooltipPosition: "top"
            },
            icon: 'pi pi-trash',
            command: () => {
                this.switchAutoRefreshSubject.next(false);
            }
        },
        {
            tooltipOptions: {
                tooltipLabel: "Open Players Screen",
                tooltipPosition: "top"
            },
            icon: 'pi pi-user',
            routerLink: ['/player']
        }
    ]
  }

  ngOnDestroy(): void {
    this.disableAutoRefresh();
    this.switchAutoRefreshSubscription?.unsubscribe();
  }

  enableAutoRefresh() {
    this.refreshPlayersTimerSubscription = this.refreshPlayersTimer.subscribe(() => this.refreshPlayers());
    this.refreshChallengesTimerSubscription = this.refreshChallengesTimer.subscribe(() => this.refreshChallenges());
  }

  disableAutoRefresh() {
    this.refreshPlayersTimerSubscription?.unsubscribe();
    this.refreshChallengesTimerSubscription?.unsubscribe();
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
    if (this.c_current) {
      this.rankingService
        .getChallengeRankings(this.c_current.id)
        .subscribe(
          (rankings: ChallengeRanking[]) => {
            this.rankingService
              .getGlobalRankings()
              .subscribe(
                (rankings: GlobalRanking[]) => {
                  rankings.sort((a, b) => a.rank - b.rank);
                  this.globalRankings = rankings;
                }
              );
            rankings.sort((a, b) => a.rank - b.rank);
            this.challengeRankings = rankings;
          }
        );
    }
  }

  refreshChallenges() {
    this.challengeService
      .getChallengeCurrent()
      .subscribe(
        (c: Challenge) => {
          this.refreshRankings();
          this.challengeService
            .getChallengeNext()
            .subscribe(
              (c: Challenge) => {
                this.c_next = c;
              }
            );
          this.challengeService
            .getChallenges()
            .subscribe(
              (challenges: Challenge[]) => {
                this.challenges = challenges;
              }
            );
          this.c_current = c;
        }
      );
  }

}
