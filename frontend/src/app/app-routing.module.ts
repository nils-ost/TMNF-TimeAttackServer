import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router'; // CLI imports router
import { WelcomeComponent } from './components/welcome/welcome.component';
import { WallboardComponent } from './components/wallboard/wallboard.component';

const routes: Routes = [
  { path: 'welcome', component: WelcomeComponent },
  { path: 'wallboard', component: WallboardComponent },
  { path: '**', component: WelcomeComponent },
];

// configures NgModule imports and exports
@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
