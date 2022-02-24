import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router'; // CLI imports router
import { ChallengesComponent } from './components/challenges/challenges.component';
import { WallboardComponent } from './components/wallboard/wallboard.component';

const routes: Routes = [
  { path: 'challenges', component: ChallengesComponent },
  { path: 'wallboard', component: WallboardComponent },
  { path: '**', component: ChallengesComponent },
];

// configures NgModule imports and exports
@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
