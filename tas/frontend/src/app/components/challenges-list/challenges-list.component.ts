import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { Challenge } from '../../interfaces/challenge';
import { Settings } from '../../interfaces/settings';
import { environment } from '../../../environments/environment';
import { Server } from 'src/app/interfaces/server';

interface SortableChallenge {
  id: string;
  server: string;
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
  @Input() servers!: Server[];
  @Input() challenges!: Challenge[];
  @Input() currentChallenges!: Challenge[];
  @Input() settings?: Settings;
  @Output() selectChallengeEvent = new EventEmitter<Challenge | null>();
  selectedChallenge?: Challenge;
  sortableChallenges: SortableChallenge[] = [];
  apiUrl: string = "";
  unpredictedUpIn: boolean = true;

  constructor() { }

  ngOnInit(): void {
    this.apiUrl = environment.apiUrl;
    this.buildSortableChallenges();
    this.calculateUnpredictedUpIn();
  }

  ngOnChanges(changes: SimpleChanges) {
    this.buildSortableChallenges();
    this.calculateUnpredictedUpIn();
  }

  selectChallenge(challenge: Challenge | null) {
    this.selectChallengeEvent.emit(challenge);
  }

  buildSortableChallenges() {
    let run_var: { [key: string]: any } = {};
    for (const s of this.servers) {
      run_var[s.id] = {
        c_index: -1,
        up_in: 0,
        up_at: 0,
        current_c: null
      }
    }
    for (const c of this.currentChallenges) {
      if (c.id && c.server in run_var) {
        run_var[c.server]['current_c'] = c;
      }
    }
    let scs: SortableChallenge[] = [];
    
    for (let i = 0; i < this.challenges.length; i++) {
      const c: Challenge = this.challenges[i];
      if (c.server in run_var && run_var[c.server]['current_c']) {
        if (run_var[c.server]['c_index'] > -1) {
          run_var[c.server]['up_in'] += Math.floor(c.time_limit / 1000);
          run_var[c.server]['up_at'] += Math.floor(c.time_limit / 1000);
          let sc: SortableChallenge = {
            id: c.id,
            server: c.server,
            name: c.name,
            seen_count: c.seen_count,
            seen_last: c.seen_last,
            time_limit: c.time_limit,
            up_in: Math.floor(run_var[c.server]['up_in'] / 60),
            up_at: run_var[c.server]['up_at']
          } as SortableChallenge;
          scs.push(sc);
        }
        if (c.id === run_var[c.server]['current_c'].id) {
          run_var[c.server]['c_index'] = i;
          run_var[c.server]['up_in'] = c.seen_last - (Math.floor(Date.now()/1000));
          run_var[c.server]['up_at'] = c.seen_last;
        }
      }
    }
    for (let i = 0; i < this.challenges.length; i++) {
      const c: Challenge = this.challenges[i];
      if (c.server in run_var  && run_var[c.server]['current_c'] && i <= run_var[c.server]['c_index']) {
        run_var[c.server]['up_in'] += Math.floor(c.time_limit / 1000);
        run_var[c.server]['up_at'] += Math.floor(c.time_limit / 1000);
        let sc: SortableChallenge = {
          id: c.id,
          server: c.server,
          name: c.name,
          seen_count: c.seen_count,
          seen_last: c.seen_last,
          time_limit: c.time_limit,
          up_in: Math.floor(run_var[c.server]['up_in'] / 60),
          up_at: run_var[c.server]['up_at']
        } as SortableChallenge;
        scs.push(sc);
      }
    }
    
    this.sortableChallenges = scs;
  }

  calculateUnpredictedUpIn() {
    let c = this.challenges.find(c => c.seen_count === 0);
    if (c) this.unpredictedUpIn = true;
    else this.unpredictedUpIn = false;
  }

}
