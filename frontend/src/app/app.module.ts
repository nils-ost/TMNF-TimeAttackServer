import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { TableModule } from 'primeng/table';

import { AppComponent } from './app.component';
import { RankingGlobalComponent } from './components/ranking-global/ranking-global.component';
import { RankingChallengeComponent } from './components/ranking-challenge/ranking-challenge.component';
import { ChallengesComponent } from './components/challenges/challenges.component';
import { WallboardComponent } from './components/wallboard/wallboard.component';
import { PlayersListComponent } from './components/players-list/players-list.component';

@NgModule({
  declarations: [
    AppComponent,
    RankingGlobalComponent,
    RankingChallengeComponent,
    ChallengesComponent,
    WallboardComponent,
    PlayersListComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    TableModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
