import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { HttpClientModule } from '@angular/common/http';
import { TableModule } from 'primeng/table';
import { RippleModule } from 'primeng/ripple';
import { SpeedDialModule } from 'primeng/speeddial';
import { CardModule } from 'primeng/card';

import { AppComponent } from './app.component';
import { RankingGlobalComponent } from './components/ranking-global/ranking-global.component';
import { RankingChallengeComponent } from './components/ranking-challenge/ranking-challenge.component';
import { WallboardComponent } from './components/wallboard/wallboard.component';
import { PlayersListComponent } from './components/players-list/players-list.component';
import { ChallengeCardComponent } from './components/challenge-card/challenge-card.component';
import { ChallengesTickerComponent } from './components/challenges-ticker/challenges-ticker.component';
import { WelcomeComponent } from './components/welcome/welcome.component';
import { PlayersComponent } from './components/players/players.component';
import { PlayersChallengeListComponent } from './components/players-challenge-list/players-challenge-list.component';
import { PlayersLaptimeListComponent } from './components/players-laptime-list/players-laptime-list.component';
import { ChallengesComponent } from './components/challenges/challenges.component';
import { ChallengesListComponent } from './components/challenges-list/challenges-list.component';

@NgModule({
  declarations: [
    AppComponent,
    RankingGlobalComponent,
    RankingChallengeComponent,
    WallboardComponent,
    PlayersListComponent,
    ChallengeCardComponent,
    ChallengesTickerComponent,
    WelcomeComponent,
    PlayersComponent,
    PlayersChallengeListComponent,
    PlayersLaptimeListComponent,
    ChallengesComponent,
    ChallengesListComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    TableModule,
    RippleModule,
    SpeedDialModule,
    CardModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
