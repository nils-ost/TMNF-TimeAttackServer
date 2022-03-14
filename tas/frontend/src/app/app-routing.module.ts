import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router'; // CLI imports router
import { WelcomeComponent } from './components/welcome/welcome.component';
import { WallboardComponent } from './components/wallboard/wallboard.component';
import { PlayersComponent } from './components/players/players.component';
import { ChallengesComponent } from './components/challenges/challenges.component';

const routes: Routes = [
  { path: 'welcome', component: WelcomeComponent },
  { path: 'wallboard', component: WallboardComponent },
  { path: 'players', component: PlayersComponent },
  { path: 'challenges', component: ChallengesComponent },
  { path: '**', component: WelcomeComponent },
];

// configures NgModule imports and exports
@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
