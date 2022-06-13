import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { Player } from '../interfaces/player';
import { PlayerRanking } from '../interfaces/ranking';
import { environment } from '../../environments/environment';
import { PlayerChallengeLaptime } from '../interfaces/laptime';
import { handleError, cleanName } from './common';

@Injectable({
  providedIn: 'root'
})
export class PlayerService {

  private playerUrl = environment.apiUrl + '/players/';

  constructor(private http: HttpClient) { }

  private cleanPlayerName(player: Player | null) {
    if (player) player.name = cleanName(player.name);
    return player;
  }

  private cleanPlayersNames(players: Player[]) {
    for (let i = 0; i < players.length; i++) {
      let newPlayer: Player | null = this.cleanPlayerName(players[i]);
      if (newPlayer) players[i] = newPlayer;
    }
    return players;
  }

  public getPlayers(): Observable<Player[]> {
    return this.http.get<Player[]>(this.playerUrl).pipe(catchError(handleError), map((players) => this.cleanPlayersNames(players)));
  }

  public getPlayerRankings(player_id: string): Observable<PlayerRanking[]> {
    return this.http.get<PlayerRanking[]>(this.playerUrl + encodeURIComponent(player_id) + '/rankings/').pipe(catchError(handleError));
  }

  public getPlayerChallengeLaptimes(player_id: string, challenge_id: string): Observable<PlayerChallengeLaptime[]> {
    return this.http.get<PlayerChallengeLaptime[]>(this.playerUrl + encodeURIComponent(player_id) + '/laptimes/' + challenge_id).pipe(catchError(handleError));
  }

  public getPlayerMe(): Observable<Player | null> {
    return this.http.get<Player | null>(this.playerUrl + 'me/').pipe(catchError(handleError), map((player) => this.cleanPlayerName(player)));
  }

  public setPlayerMe(player_id: string): Observable<any> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type':  'application/json'
      })
    };
    return this.http.patch<any>(this.playerUrl + 'me/', {'player_id': player_id}, httpOptions).pipe(catchError(handleError));
  }
}
