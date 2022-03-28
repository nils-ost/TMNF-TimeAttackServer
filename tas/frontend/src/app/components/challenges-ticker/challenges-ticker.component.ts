import { Component, Input, Output, EventEmitter, OnInit, OnDestroy } from '@angular/core';
import { Challenge, ChallengeDisplay } from '../../interfaces/challenge';
import { Subscription, timer, Observable } from 'rxjs';

@Component({
  selector: 'app-challenges-ticker',
  templateUrl: './challenges-ticker.component.html',
  styleUrls: ['./challenges-ticker.component.scss']
})
export class ChallengesTickerComponent implements OnInit, OnDestroy {
  @Input() challenges!: Challenge[];
  @Input() current_challenge_id!: string;
  @Input() next_challenge_id!: string;
  @Input() switchAutoRefreshEvent!: Observable<boolean>;
  @Output() onEnableRefresh = new EventEmitter();
  @Output() onDisableRefresh = new EventEmitter();
  challengeDisplay: ChallengeDisplay[] = [];

  refreshChallengeDisplayTimer = timer(1000, 10000);
  refreshChallengeDisplayTimerSubscription: Subscription | undefined;
  switchAutoRefreshSubscription: Subscription | undefined;

  constructor() { }

  ngOnInit(): void {
    this.refreshChallengeDisplay();
    this.enableAutoRefresh();

    this.switchAutoRefreshSubscription = this.switchAutoRefreshEvent.subscribe(
      (switchOn) => {
        if (switchOn) this.enableAutoRefresh();
        else this.disableAutoRefresh();
      }
    );
  }

  ngOnDestroy(): void {
    this.disableAutoRefresh();
    this.switchAutoRefreshSubscription?.unsubscribe();
  }

  enableAutoRefresh() {
    this.refreshChallengeDisplayTimerSubscription = this.refreshChallengeDisplayTimer.subscribe(() => this.refreshChallengeDisplay());
  }

  disableAutoRefresh() {
    this.refreshChallengeDisplayTimerSubscription?.unsubscribe();
  }

  refreshChallengeDisplay() {
    let max_elements = 8;
    let tmp: ChallengeDisplay[] = [];
    let current_index: number = -1;
    let up_in: number = 0;
    for (let i = 0; i < this.challenges.length; i++) {
      let c: Challenge = this.challenges[i];
      let cd: ChallengeDisplay = {
        id: c.id,
        name: c.name,
        seen_count: c.seen_count,
        time_limit: Math.floor(c.time_limit / 1000),
        is_current: c.id === this.current_challenge_id,
        is_next: c.id === this.next_challenge_id,
        is_loading: false,
        up_in: ""
      } as ChallengeDisplay;
      if (c.id === this.current_challenge_id) {
        current_index = i;
        up_in = (c.time_limit / 1000) - (Math.floor(Date.now()/1000) - c.seen_last);
      } else if (current_index != -1) {
        if (up_in > 60) cd.up_in = "~" + Math.floor(up_in / 60).toString() + "m";
        else cd.up_in = "<1m";
        if (up_in < 0) cd.is_loading = true;
        up_in += c.time_limit / 1000;
      }
      if (current_index != -1 && tmp.length < max_elements) tmp.push(cd);
      if (tmp.length >= max_elements) break;
    }
    if (current_index != -1 && tmp.length < max_elements) {
      for(let i = 0; i < current_index; i++) {
        let c: Challenge = this.challenges[i];
        let cd: ChallengeDisplay = {
          id: c.id,
          name: c.name,
          seen_count: c.seen_count,
          time_limit: Math.floor(c.time_limit / 1000),
          is_current: c.id === this.current_challenge_id,
          is_next: c.id === this.next_challenge_id,
          is_loading: false,
          up_in: ""
        } as ChallengeDisplay;
        if (up_in > 60) cd.up_in = "~" + Math.floor(up_in / 60).toString() + "m";
        else cd.up_in = "<1m";
        if (up_in < 0) cd.is_loading = true;
        up_in += cd.time_limit;
        if (tmp.length < max_elements) tmp.push(cd);
        if (tmp.length >= max_elements) break;
      }
    }
    this.challengeDisplay = tmp;
  }

}
