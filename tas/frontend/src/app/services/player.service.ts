import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Player } from '../interfaces/player';
import { PlayerRanking } from '../interfaces/ranking';
import { environment } from '../../environments/environment';
import { PlayerChallengeLaptime } from '../interfaces/laptime';

@Injectable({
  providedIn: 'root'
})
export class PlayerService {

  private playerUrl = environment.apiUrl + '/players/';

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

  public getPlayers(): Observable<Player[]> {
    return this.http.get<Player[]>(this.playerUrl).pipe(catchError(this.handleError));
  }

  public getPlayerRankings(player_id: string): Observable<PlayerRanking[]> {
    return this.http.get<PlayerRanking[]>(this.playerUrl + player_id + '/rankings/').pipe(catchError(this.handleError));
  }

  public getPlayerChallengeLaptimes(player_id: string, challenge_id: string): Observable<PlayerChallengeLaptime[]> {
    return this.http.get<PlayerChallengeLaptime[]>(this.playerUrl + player_id + '/laptimes/' + challenge_id).pipe(catchError(this.handleError));
  }
}
