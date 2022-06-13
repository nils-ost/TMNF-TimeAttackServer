import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Settings } from '../interfaces/settings';
import { environment } from '../../environments/environment';
import { handleError } from './common';

@Injectable({
  providedIn: 'root'
})
export class SettingsService {

  private settignsUrl = environment.apiUrl + '/settings/';

  constructor(private http: HttpClient) { }

  public getSettings(): Observable<Settings> {
    return this.http.get<Settings>(this.settignsUrl).pipe(catchError(handleError));
  }
}
