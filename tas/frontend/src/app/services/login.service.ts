import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Login } from '../interfaces/login';
import { environment } from '../../environments/environment';
import { Md5 } from 'ts-md5';

@Injectable({
  providedIn: 'root'
})
export class LoginService {

  private loginUrl = environment.apiUrl + '/login/';

  constructor(private http: HttpClient) { }

  public getLogin(): Observable<Login> {
    return this.http.get<Login>(this.loginUrl, {withCredentials:true}).pipe(catchError(this.handleError));
  }

  public startLogin(username: string): Observable<Login> {
    return this.http.get<Login>(this.loginUrl + "?user=" + username, {withCredentials:true}).pipe(catchError(this.handleError));
  }

  public completeLogin(session_id: string, password: string): Observable<Login> {
    let md5 = new Md5();
    let pw = md5.appendStr(session_id).appendStr(password).end()
    return this.http.post<Login>(this.loginUrl, {'pw': pw}, {withCredentials:true}).pipe(catchError(this.handleError));
  }

  public logout(): Observable<any> {
    return this.http.put<any>(this.loginUrl, {}, {withCredentials:true}).pipe(catchError(this.handleError));
  }

  private handleError(error: HttpErrorResponse) {
    if (error.status === 0) {
      console.error('An error occurred:', error.error);
    } else {
      console.error(`Backend returned code ${error.status}, body was: `, error.error);
    }
    let login: Login = {};
    return of(login);
  }
}
