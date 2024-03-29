import { Component, Input, Output, EventEmitter, OnInit, OnDestroy } from '@angular/core';
import { Router } from "@angular/router"
import { Challenge, ChallengeDisplay } from '../../interfaces/challenge';
import { Subscription, timer, Observable } from 'rxjs';
import { Settings } from '../../interfaces/settings';
import { Server } from 'src/app/interfaces/server';

@Component({
  selector: 'app-challenges-ticker',
  templateUrl: './challenges-ticker.component.html',
  styleUrls: ['./challenges-ticker.component.scss']
})
export class ChallengesTickerComponent implements OnInit, OnDestroy {
  @Input() challenges!: Challenge[];
  @Input() settings?: Settings;
  @Input() currentChallenges: { [key: string]: Challenge } = {};
  @Input() nextChallenges: { [key: string]: Challenge } = {};
  @Input() servers: Server[] = [];
  @Input() switchAutoRefreshEvent!: Observable<boolean>;
  @Output() onEnableRefresh = new EventEmitter();
  @Output() onDisableRefresh = new EventEmitter();
  challengeDisplay: { [key: string]: ChallengeDisplay[] } = {};
  time_left: number = 9999;
  redirect_in: number = 20;

  refreshChallengeDisplayTimer = timer(1000, 10000);
  refreshRedirectTimer = timer(1000, 1000);
  refreshChallengeDisplayTimerSubscription: Subscription | undefined;
  refreshRedirectTimerSubscription: Subscription | undefined;
  switchAutoRefreshSubscription: Subscription | undefined;

  constructor(
    private router: Router
  ) { }

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
    this.refreshRedirectTimerSubscription?.unsubscribe();
  }

  refreshRedirectIn() {
    this.redirect_in -= 1;
    if (this.redirect_in <= 0) this.router.navigate(['/players']);
  }

  refreshChallengeDisplay() {
    let max_elements = 2;
    if (this.settings) {
      if (this.servers.length > 0)
        max_elements = Math.floor(this.settings.wallboard_challenges_max / this.servers.length);
      if (max_elements < 2) max_elements = 2;
      if (this.settings.end_time) {
        this.time_left = this.settings.end_time - Math.floor(Date.now()/1000);
        if (this.time_left <= 0) {
          this.refreshChallengeDisplayTimerSubscription?.unsubscribe();
          this.redirect_in = 20;
          this.refreshRedirectTimerSubscription = this.refreshRedirectTimer.subscribe(() => this.refreshRedirectIn());
        }
      }
    }
    
    for (let server of this.servers) {
      let currentChallenge: Challenge = this.currentChallenges[server.id];
      let nextChallenge: Challenge = this.nextChallenges[server.id];
      let tmp: ChallengeDisplay[] = [];
      let current_index: number = -1;
      let up_in: number = 0;
      for (let i = 0; i < this.challenges.length; i++) {
        let c: Challenge = this.challenges[i];
        if (c.server != server.id) continue;
        let cd: ChallengeDisplay = {
          id: c.id,
          name: c.name,
          seen_count: c.seen_count,
          time_limit: Math.floor(c.time_limit / 1000),
          is_current: c.id === currentChallenge.id,
          is_next: c.id === nextChallenge.id,
          is_loading: false,
          up_in: ""
        } as ChallengeDisplay;
        if (c.id === currentChallenge.id) {
          current_index = i;
          up_in = (c.time_limit / 1000) - (Math.floor(Date.now()/1000) - c.seen_last);
        } else if (current_index != -1) {
          if (up_in > 60) cd.up_in = "~" + Math.floor(up_in / 60).toString() + "m";
          else cd.up_in = "<1m";
          if (up_in < 0) cd.is_loading = true;
          up_in += c.time_limit / 1000;
        }
        if (current_index != -1 && tmp.length < max_elements && (up_in - c.time_limit / 1000) < this.time_left) tmp.push(cd);
        if (tmp.length >= max_elements) break;
      }
      if (current_index != -1 && tmp.length < max_elements) {
        for(let i = 0; i < current_index; i++) {
          let c: Challenge = this.challenges[i];
          if (c.server != server.id) continue;
          let cd: ChallengeDisplay = {
            id: c.id,
            name: c.name,
            seen_count: c.seen_count,
            time_limit: Math.floor(c.time_limit / 1000),
            is_current: c.id === currentChallenge.id,
            is_next: c.id === nextChallenge.id,
            is_loading: false,
            up_in: ""
          } as ChallengeDisplay;
          if (up_in > 60) cd.up_in = "~" + Math.floor(up_in / 60).toString() + "m";
          else cd.up_in = "<1m";
          if (up_in < 0) cd.is_loading = true;
          up_in += cd.time_limit;
          if (tmp.length < max_elements && (up_in - c.time_limit / 1000) < this.time_left) tmp.push(cd);
          if (tmp.length >= max_elements) break;
        }
      }
      this.challengeDisplay[server.id] = tmp;
    }
  }

}
