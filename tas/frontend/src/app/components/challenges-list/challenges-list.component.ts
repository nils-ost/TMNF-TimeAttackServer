import { Component, Input, OnInit } from '@angular/core';
import { Challenge } from '../../interfaces/challenge';

@Component({
  selector: 'app-challenges-list',
  templateUrl: './challenges-list.component.html',
  styleUrls: ['./challenges-list.component.scss']
})
export class ChallengesListComponent implements OnInit {
  @Input() challenges!: Challenge[];
  @Input() currentChallenge!: Challenge;

  constructor() { }

  ngOnInit(): void {
  }

}
