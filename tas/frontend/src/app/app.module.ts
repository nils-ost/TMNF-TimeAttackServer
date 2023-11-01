import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AppRoutingModule } from './app-routing.module';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { TableModule } from 'primeng/table';
import { RippleModule } from 'primeng/ripple';
import { SpeedDialModule } from 'primeng/speeddial';
import { DialogModule } from 'primeng/dialog';
import { DropdownModule } from 'primeng/dropdown';
import { ButtonModule } from 'primeng/button';
import { MessagesModule } from 'primeng/messages';
import { MessageModule } from 'primeng/message';
import { ImageModule } from 'primeng/image';
import { ListboxModule } from 'primeng/listbox';
import { TooltipModule } from 'primeng/tooltip';
import { InputTextModule } from 'primeng/inputtext';
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
import { ChallengesPlayerListComponent } from './components/challenges-player-list/challenges-player-list.component';
import { PlayerhudComponent } from './components/playerhud/playerhud.component';
import { PlayerhudCurrentListComponent } from './components/playerhud-current-list/playerhud-current-list.component';
import { PlayerhudGlobalListComponent } from './components/playerhud-global-list/playerhud-global-list.component';
import { StartCountdownComponent } from './components/start-countdown/start-countdown.component';
import { EndCountdownComponent } from './components/end-countdown/end-countdown.component';
import { HotseatNameScreenComponent } from './components/hotseat-name-screen/hotseat-name-screen.component';
import { AutoFocusDirective } from './directives/auto-focus.directive';
import { HotseatWallboardScreenComponent } from './components/hotseat-wallboard-screen/hotseat-wallboard-screen.component';
import { HotseatRankingChallengeComponent } from './components/hotseat-ranking-challenge/hotseat-ranking-challenge.component';
import { AdminScreenComponent } from './components/admin-screen/admin-screen.component';
import { LoginComponent } from './components/login/login.component';

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
    ChallengesListComponent,
    ChallengesPlayerListComponent,
    PlayerhudComponent,
    PlayerhudCurrentListComponent,
    PlayerhudGlobalListComponent,
    StartCountdownComponent,
    EndCountdownComponent,
    HotseatNameScreenComponent,
    AutoFocusDirective,
    HotseatWallboardScreenComponent,
    HotseatRankingChallengeComponent,
    AdminScreenComponent,
    LoginComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    TableModule,
    RippleModule,
    SpeedDialModule,
    DialogModule,
    DropdownModule,
    ButtonModule,
    MessagesModule,
    MessageModule,
    ImageModule,
    ListboxModule,
    TooltipModule,
    InputTextModule,
    CardModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
