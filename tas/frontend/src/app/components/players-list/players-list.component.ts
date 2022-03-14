import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { Player } from '../../interfaces/player';
import { GlobalRanking } from '../../interfaces/ranking';

interface SortablePlayer {
    id: string;
    name: string;
    last_update: number;
    rank: number;
    points: number;
}

@Component({
  selector: 'app-players-list',
  templateUrl: './players-list.component.html',
  styleUrls: ['./players-list.component.css']
})
export class PlayersListComponent implements OnInit, OnChanges {

  @Input() players!: Player[];
  @Input() globalRankings!: GlobalRanking[];
  @Output() selectPlayerEvent = new EventEmitter<Player | null>();
  selectedPlayer?: Player;
  sortablePlayers: SortablePlayer[] = [];

  constructor() { }

  ngOnInit(): void {
    this.buildSortablePlayers();
  }

  ngOnChanges(changes: SimpleChanges) {
    this.buildSortablePlayers();
  }

  selectPlayer(player: Player | null) {
    this.selectPlayerEvent.emit(player);
  }

  playerRank(player_id: string): number {
    let r = this.globalRankings.find(r => r.player_id === player_id);
    if (r) return r.rank;
    else return 999;
  }

  playerPoints(player_id: string): number {
    let r = this.globalRankings.find(r => r.player_id === player_id);
    if (r) return r.points;
    else return 0;
  }

  buildSortablePlayers() {
    let new_sp: SortablePlayer[] = [];
    for (let i = 0; i < this.players.length; i++) {
      let sp: SortablePlayer = {
        id: this.players[i].id,
        name: this.players[i].name,
        last_update: this.players[i].last_update,
        rank: this.playerRank(this.players[i].id),
        points: this.playerPoints(this.players[i].id)
      } as SortablePlayer;
      new_sp.push(sp);
    }
    this.sortablePlayers = new_sp;
  }

}
