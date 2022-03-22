import { Component, Input, OnInit } from '@angular/core';
import { ChallengeDisplay } from '../../interfaces/challenge';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-challenge-card',
  templateUrl: './challenge-card.component.html',
  styleUrls: ['./challenge-card.component.scss']
})
export class ChallengeCardComponent implements OnInit {
  @Input() challenge!: ChallengeDisplay;
  thumbnailUrl: string = "";

  constructor() { }

  ngOnInit(): void {
    this.thumbnailUrl = environment.apiUrl + '/thumbnails/' + this.challenge.id + '.jpg';
  }

}
