import { Component, Input, OnInit } from '@angular/core';
import { ChallengeDisplay } from '../../interfaces/challenge';

@Component({
  selector: 'app-challenge-card',
  templateUrl: './challenge-card.component.html',
  styleUrls: ['./challenge-card.component.scss']
})
export class ChallengeCardComponent implements OnInit {
  @Input() challenge!: ChallengeDisplay;

  constructor() { }

  ngOnInit(): void {
  }

}
