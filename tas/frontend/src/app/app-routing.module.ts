import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router'; // CLI imports router
import { WelcomeComponent } from './components/welcome/welcome.component';
import { WallboardComponent } from './components/wallboard/wallboard.component';
import { PlayersComponent } from './components/players/players.component';
import { ChallengesComponent } from './components/challenges/challenges.component';
import { PlayerhudComponent } from './components/playerhud/playerhud.component';
import { StartCountdownComponent } from './components/start-countdown/start-countdown.component';
import { EndCountdownComponent } from './components/end-countdown/end-countdown.component';
import { HotseatNameScreenComponent } from './components/hotseat-name-screen/hotseat-name-screen.component';
import { HotseatWallboardScreenComponent } from './components/hotseat-wallboard-screen/hotseat-wallboard-screen.component';
import { AdminScreenComponent } from './components/admin-screen/admin-screen.component';
import { LoginComponent } from './components/login/login.component';

const routes: Routes = [
  { path: 'welcome', component: WelcomeComponent },
  { path: 'wallboard', component: WallboardComponent },
  { path: 'players', component: PlayersComponent },
  { path: 'challenges', component: ChallengesComponent },
  { path: 'playerhud', component: WelcomeComponent },
  { path: 'start-countdown', component: StartCountdownComponent },
  { path: 'end-countdown', component: EndCountdownComponent },
  { path: 'hotseat-name', component: HotseatNameScreenComponent },
  { path: 'hotseat-wallboard', component: HotseatWallboardScreenComponent },
  { path: 'admin', component: AdminScreenComponent },
  { path: 'login', component: LoginComponent },
  { path: '**', component: WelcomeComponent },
];

// configures NgModule imports and exports
@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
