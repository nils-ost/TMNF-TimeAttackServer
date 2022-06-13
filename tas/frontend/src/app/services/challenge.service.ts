import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { Challenge } from '../interfaces/challenge';
import { environment } from '../../environments/environment';
import { handleError, cleanName } from './common';

@Injectable({
  providedIn: 'root'
})
export class ChallengeService {

  private challengeUrl = environment.apiUrl + '/challenges/';

  constructor(private http: HttpClient) { }

  private cleanChallengeName(challenge: Challenge | null) {
    if (challenge) challenge.name = cleanName(challenge.name);
    return challenge;
  }

  private cleanChallengesNames(challenges: Challenge[]) {
    for (let i = 0; i < challenges.length; i++) {
      let newChallenge: Challenge | null = this.cleanChallengeName(challenges[i]);
      if (newChallenge) challenges[i] = newChallenge;
    }
    return challenges;
  }

  public getChallenges(): Observable<Challenge[]> {
    return this.http.get<Challenge[]>(this.challengeUrl).pipe(catchError(handleError), map((challenges) => this.cleanChallengesNames(challenges)));
  }

  getChallengeCurrent(): Observable<Challenge | null> {
    return this.http.get<Challenge>(this.challengeUrl + "current").pipe(catchError(handleError), map((challenge) => this.cleanChallengeName(challenge)));
  }

  getChallengeNext(): Observable<Challenge | null> {
    return this.http.get<Challenge>(this.challengeUrl + "next").pipe(catchError(handleError), map((challenge) => this.cleanChallengeName(challenge)));
  }
}
