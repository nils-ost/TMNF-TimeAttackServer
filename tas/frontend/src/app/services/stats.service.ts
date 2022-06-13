import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Stats } from '../interfaces/stats';
import { environment } from '../../environments/environment';
import { handleError } from './common';

@Injectable({
  providedIn: 'root'
})
export class StatsService {

  private settignsUrl = environment.apiUrl + '/stats/';

  constructor(private http: HttpClient) { }

  public getStats(): Observable<Stats> {
    return this.http.get<Stats>(this.settignsUrl).pipe(catchError(handleError));
  }
}
