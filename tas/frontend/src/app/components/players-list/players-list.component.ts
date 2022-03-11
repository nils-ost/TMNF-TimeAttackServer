import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { Player } from '../../interfaces/player';

@Component({
  selector: 'app-players-list',
  templateUrl: './players-list.component.html',
  styleUrls: ['./players-list.component.css']
})
export class PlayersListComponent implements OnInit {

  @Input() players!: Player[];
  @Output() selectPlayerEvent = new EventEmitter<Player | null>();
  selectedPlayer?: Player;

  constructor() { }

  ngOnInit(): void {
  }

  selectPlayer(player: Player | null) {
    this.selectPlayerEvent.emit(player);
  }

}
