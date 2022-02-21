import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Challenge } from '../interfaces/challenge';

@Injectable({
  providedIn: 'root'
})
export class ChallengeService {

  private challengeUrl = 'http://192.168.56.102:8000/challenges/';

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
}
