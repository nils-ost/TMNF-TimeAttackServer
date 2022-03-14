import { Component, OnInit } from '@angular/core';
import { ChallengeService } from '../../services/challenge.service';
import { Challenge } from '../../interfaces/challenge';

@Component({
  selector: 'app-challenges',
  templateUrl: './challenges.component.html',
  styleUrls: ['./challenges.component.scss']
})
export class ChallengesComponent implements OnInit {
  challenges: Challenge[] = [];
  currentChallenge?: Challenge;

  constructor(
    private challengeService: ChallengeService
  ) { }

  ngOnInit(): void {
    this.refreshChallenges();
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

}
