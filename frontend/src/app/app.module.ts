import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { TableModule } from 'primeng/table';
import { CardModule } from 'primeng/card';
import { CarouselModule } from 'primeng/carousel';

import { AppComponent } from './app.component';
import { RankingGlobalComponent } from './components/ranking-global/ranking-global.component';
import { RankingChallengeComponent } from './components/ranking-challenge/ranking-challenge.component';
import { ChallengesComponent } from './components/challenges/challenges.component';
import { WallboardComponent } from './components/wallboard/wallboard.component';
import { PlayersListComponent } from './components/players-list/players-list.component';
import { ChallengeCardComponent } from './components/challenge-card/challenge-card.component';
import { ChallengesTickerComponent } from './components/challenges-ticker/challenges-ticker.component';

@NgModule({
  declarations: [
    AppComponent,
    RankingGlobalComponent,
    RankingChallengeComponent,
    ChallengesComponent,
    WallboardComponent,
    PlayersListComponent,
    ChallengeCardComponent,
    ChallengesTickerComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    TableModule,
    CardModule,
    CarouselModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
