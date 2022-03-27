import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges, ViewChild } from '@angular/core';
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
  @ViewChild('dt') table: any;
  selectedPlayer?: Player;
  sortablePlayers: SortablePlayer[] = [];
  cols: any[] = [
    { field: 'rank', header: $localize `:Header for column rank in tables@@tableHeaderRank:rank` },
    { field: 'id', header: $localize `:Header for column player id in tables@@tableHeaderPlayerID:id` },
    { field: 'name', header: $localize `:Header for column player name in tables@@tableHeaderPlayerName:player` },
    { field: 'last_update', header: $localize `:Header for column last update in tables@@tableHeaderLastUpdate:last update` },
    { field: 'points', header: $localize `:Header for column points in tables@@tableHeaderPoints:points` }
  ];

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

  exportCSV() {
    this.table.exportCSV();
  }

}
