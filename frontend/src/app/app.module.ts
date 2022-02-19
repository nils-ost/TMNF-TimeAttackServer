import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent } from './app.component';
import { RankingGlobalComponent } from './components/ranking-global/ranking-global.component';
import { RankingChallengeComponent } from './components/ranking-challenge/ranking-challenge.component';

@NgModule({
  declarations: [
    AppComponent,
    RankingGlobalComponent,
    RankingChallengeComponent
  ],
  imports: [
    BrowserModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
