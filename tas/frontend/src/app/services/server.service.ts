import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { Server } from '../interfaces/server';
import { Observable, catchError } from 'rxjs';
import { handleError } from './common';

@Injectable({
  providedIn: 'root'
})
export class ServerService {

  private serversUrl = environment.apiUrl + '/servers/';

  constructor(private http: HttpClient) { }

  getServers(): Observable<Server[]> {
    return this.http.get<Server[]>(this.serversUrl).pipe(catchError(handleError));
  }
}
