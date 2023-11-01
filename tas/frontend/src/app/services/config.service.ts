import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { Config } from '../interfaces/config';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {

  private configurl = environment.apiUrl + '/config/';

  constructor(
    private http: HttpClient
  ) { }

  public getConfig(id: string): Observable<Config> {
    return this.http.get<Config>(this.configurl + id + '/', {withCredentials:true});
  }

  public getConfigs(): Observable<Config[]> {
    return this.http.get<Config[]>(this.configurl, {withCredentials:true});
  }
}
