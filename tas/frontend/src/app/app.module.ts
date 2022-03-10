import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { HttpClientModule } from '@angular/common/http';
import { TableModule } from 'primeng/table';
import { RippleModule } from 'primeng/ripple';
import { SpeedDialModule } from 'primeng/speeddial';

import { AppComponent } from './app.component';
import { RankingGlobalComponent } from './components/ranking-global/ranking-global.component';
import { RankingChallengeComponent } from './components/ranking-challenge/ranking-challenge.component';
import { WallboardComponent } from './components/wallboard/wallboard.component';
import { PlayersListComponent } from './components/players-list/players-list.component';
import { ChallengeCardComponent } from './components/challenge-card/challenge-card.component';
import { ChallengesTickerComponent } from './components/challenges-ticker/challenges-ticker.component';
import { WelcomeComponent } from './components/welcome/welcome.component';
import { PlayersComponent } from './components/players/players.component';

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
    PlayersComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    TableModule,
    RippleModule,
    SpeedDialModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
