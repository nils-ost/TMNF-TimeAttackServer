import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Challenge } from '../interfaces/challenge';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ChallengeService {

  private challengeUrl = environment.apiUrl + '/challenges/';

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

  public getChallenges(): Observable<Challenge[]> {
    return this.http.get<Challenge[]>(this.challengeUrl).pipe(catchError(this.handleError));
  }

  getChallengeCurrent(): Observable<Challenge | null> {
    return this.http.get<Challenge>(this.challengeUrl + "current").pipe(catchError(this.handleError));
  }

  getChallengeNext(): Observable<Challenge | null> {
    return this.http.get<Challenge>(this.challengeUrl + "next").pipe(catchError(this.handleError));
  }
}
