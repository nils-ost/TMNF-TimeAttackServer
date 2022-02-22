import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { GlobalRanking, ChallengeRanking } from '../interfaces/ranking';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class RankingService {

  private rankingUrl = environment.apiUrl + '/rankings/';

  constructor(private http: HttpClient) { }

  private handleError(error: HttpErrorResponse) {
  if (error.status === 0) {
    // A client-side or network error occurred. Handle it accordingly.
    console.error('An error occurred:', error.error);
  } else {
    // The backend returned an unsuccessful response code.
    // The response body may contain clues as to what went wrong.
    console.error(
      `Backend returned code ${error.status}, body was: `, error.error);
  }
    // Return an observable with a user-facing error message.
    return throwError(() => new Error('Something bad happened; please try again later.'));
  }

  getGlobalRankings(): Observable<GlobalRanking[]> {
    return this.http.get<GlobalRanking[]>(this.rankingUrl).pipe(catchError(this.handleError));
  }

  getChallengeRankings(challenge_id: string): Observable<ChallengeRanking[]> {
    return this.http.get<ChallengeRanking[]>(this.rankingUrl + challenge_id).pipe(catchError(this.handleError));
  }
}
