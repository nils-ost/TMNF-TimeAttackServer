import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { GlobalRanking, ChallengeRanking } from '../interfaces/ranking';
import { environment } from '../../environments/environment';
import { handleError } from './common';

@Injectable({
  providedIn: 'root'
})
export class RankingService {

  private rankingUrl = environment.apiUrl + '/rankings/';

  constructor(private http: HttpClient) { }

  getGlobalRankings(): Observable<GlobalRanking[]> {
    return this.http.get<GlobalRanking[]>(this.rankingUrl).pipe(catchError(handleError));
  }

  getChallengeRankings(challenge_id: string): Observable<ChallengeRanking[]> {
    return this.http.get<ChallengeRanking[]>(this.rankingUrl + challenge_id).pipe(catchError(handleError));
  }
}
