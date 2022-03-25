import { Component, OnInit } from '@angular/core';
import { ChallengeService } from '../../services/challenge.service';
import { RankingService } from '../../services/ranking.service';
import { PlayerService } from '../../services/player.service';
import { Challenge } from '../../interfaces/challenge';
import { ChallengeRanking } from '../../interfaces/ranking';
import { PlayerChallengeLaptime } from '../../interfaces/laptime';
import { Player } from '../../interfaces/player';
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-challenges',
  templateUrl: './challenges.component.html',
  styleUrls: ['./challenges.component.scss']
})
export class ChallengesComponent implements OnInit {
  challenges: Challenge[] = [];
  currentChallenge?: Challenge;
  selectedChallenge?: Challenge;
  selectedChallengeRanking?: ChallengeRanking;
  challengeRankings: ChallengeRanking[] = [];
  playerChallengeLaptimes: PlayerChallengeLaptime[] = [];
  players: Player[] = [];
  speeddail_menu: MenuItem[] = [];

  constructor(
    private challengeService: ChallengeService,
    private rankingService: RankingService,
    private playerService: PlayerService
  ) { }

  ngOnInit(): void {
    this.refreshChallenges();
    this.refreshPlayers();

    this.speeddail_menu = [
      {
        tooltipOptions: {
          tooltipLabel: "Refresh Screen",
          tooltipPosition: "top"
        },
        icon: 'pi pi-refresh',
        command: () => {
          this.refreshAll();
        }
      },
      {
        tooltipOptions: {
          tooltipLabel: "Open PlayerHUD",
          tooltipPosition: "top"
        },
        icon: 'pi pi-user',
        routerLink: ['/playerhud']
      },
      {
        tooltipOptions: {
          tooltipLabel: "Open Players Screen",
          tooltipPosition: "top"
        },
        icon: 'pi pi-users',
        routerLink: ['/players']
      },
      {
        tooltipOptions: {
          tooltipLabel: "Open Wallboard",
          tooltipPosition: "top"
        },
        icon: 'pi pi-window-maximize',
        routerLink: ['/wallboard']
      },
      {
        tooltipOptions: {
          tooltipLabel: "Open Home Screen",
          tooltipPosition: "top"
        },
        icon: 'pi pi-home',
        routerLink: ['/']
      }
    ]
  }

  selectChallenge(event: any) {
    this.selectedChallengeRanking = undefined;
    this.playerChallengeLaptimes = [];
    if (event) {
      this.selectedChallenge = event.data
      this.refreshChallengeRankings();
    }
    else {
      this.selectedChallenge = undefined;
      this.challengeRankings = [];
    }
  }

  selectChallengeRanking(event: any) {
    if (event) {
      this.selectedChallengeRanking = event.data;
      this.refreshPlayerChallengeLaptimes();
    }
    else {
      this.selectedChallengeRanking = undefined;
      this.playerChallengeLaptimes = [];
    }
  }

  refreshChallenges() {
    this.challengeService
      .getChallenges()
      .subscribe(
        (challenges: Challenge[]) => {
          this.challenges = challenges;
        }
      );
    this.challengeService
      .getChallengeCurrent()
      .subscribe(
        (c: Challenge) => {
          this.currentChallenge = c;
        }
      );
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

  refreshChallengeRankings() {
    if (this.selectedChallenge) {
      this.rankingService
        .getChallengeRankings(this.selectedChallenge.id)
        .subscribe(
          (rankings: ChallengeRanking[]) => {
            this.challengeRankings = rankings;
          }
        );
    }
  }

  refreshPlayerChallengeLaptimes() {
    if (this.selectedChallenge && this.selectedChallengeRanking) {
      this.playerService
        .getPlayerChallengeLaptimes(this.selectedChallengeRanking.player_id, this.selectedChallenge.id)
        .subscribe(
          (laptimes: PlayerChallengeLaptime[]) => {
            this.playerChallengeLaptimes = laptimes;
          }
        );
    }
  }

  refreshAll() {
    this.refreshChallenges();
    this.refreshPlayers();
    this.refreshChallengeRankings();
    this.refreshPlayerChallengeLaptimes();
  }

}
