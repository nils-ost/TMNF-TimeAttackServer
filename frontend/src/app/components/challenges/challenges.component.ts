import { Component, OnInit, OnDestroy } from '@angular/core';
import { Challenge } from '../../interfaces/challenge';
import { ChallengeService } from '../../services/challenge.service';
import { timer } from 'rxjs';

@Component({
  selector: 'app-challenges',
  templateUrl: './challenges.component.html',
  styleUrls: ['./challenges.component.css']
})
export class ChallengesComponent implements OnInit {
  private refreshTimer = timer(10000, 10000);
  private refreshTimerSubscription = this.refreshTimer.subscribe(() => this.refreshData());

  challenges: Challenge[] = [];

  constructor(
    private challengeService: ChallengeService,
  ) { }

  ngOnInit(): void {
    this.refreshData();
  }

  refreshData() {
    this.challengeService
      .getChallenges()
      .subscribe(
        (challenges: Challenge[]) => {
          this.challenges = challenges;
        }
      );
  }

}
