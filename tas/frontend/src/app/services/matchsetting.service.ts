import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { Observable, catchError } from 'rxjs';
import { handleError } from './common';

@Injectable({
  providedIn: 'root'
})
export class MatchsettingService {

  private matchsettingsUrl = environment.apiUrl + '/matchsettings/';

  constructor(private http: HttpClient) { }

  getMatchsettings(): Observable<string[]> {
    return this.http.get<string[]>(this.matchsettingsUrl).pipe(catchError(handleError));
  }
}
