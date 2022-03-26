import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { Challenge } from '../../interfaces/challenge';
import { environment } from '../../../environments/environment';

interface SortableChallenge {
  id: string;
  name: string;
  seen_count: number;
  seen_last: number;
  time_limit: number;
  up_in: number;
  up_at: number;
}

@Component({
  selector: 'app-challenges-list',
  templateUrl: './challenges-list.component.html',
  styleUrls: ['./challenges-list.component.scss']
})
export class ChallengesListComponent implements OnInit, OnChanges {
  @Input() challenges!: Challenge[];
  @Input() currentChallenge!: Challenge;
  @Output() selectChallengeEvent = new EventEmitter<Challenge | null>();
  selectedChallenge?: Challenge;
  sortableChallenges: SortableChallenge[] = [];
  thumbnailUrlBase: string = "";

  constructor() { }

  ngOnInit(): void {
    this.thumbnailUrlBase = environment.apiUrl + '/thumbnails/';
    this.buildSortableChallenges();
  }

  ngOnChanges(changes: SimpleChanges) {
    this.buildSortableChallenges();
  }

  selectChallenge(challenge: Challenge | null) {
    this.selectChallengeEvent.emit(challenge);
  }

  buildSortableChallenges() {
    if (this.currentChallenge) {
      let scs: SortableChallenge[] = [];
      let c_index = -1;
      let up_in = 0;
      let up_at = 0;
      for (let i = 0; i < this.challenges.length; i++) {
        let c: Challenge = this.challenges[i];
        if (c_index > -1) {
          up_in += Math.floor(c.time_limit / 1000);
          up_at += Math.floor(c.time_limit / 1000);
          let sc: SortableChallenge = {
            id: c.id,
            name: c.name,
            seen_count: c.seen_count,
            seen_last: c.seen_last,
            time_limit: c.time_limit,
            up_in: Math.floor(up_in / 60),
            up_at: up_at
          } as SortableChallenge;
          scs.push(sc);
        }
        if (c.id === this.currentChallenge.id) {
          c_index = i;
          up_in = c.seen_last - (Math.floor(Date.now()/1000));
          up_at = c.seen_last;
        }
      }
      for (let i = 0; i <= c_index; i++) {
        let c: Challenge = this.challenges[i];
        up_in += Math.floor(c.time_limit / 1000);
        up_at += Math.floor(c.time_limit / 1000);
        let sc: SortableChallenge = {
          id: c.id,
          name: c.name,
          seen_count: c.seen_count,
          seen_last: c.seen_last,
          time_limit: c.time_limit,
          up_in: Math.floor(up_in / 60),
          up_at: up_at
        } as SortableChallenge;
        scs.push(sc);
      }
      this.sortableChallenges = scs;
    }
  }

}
