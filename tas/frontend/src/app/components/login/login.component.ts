import { Component, OnInit } from '@angular/core';
import { Login } from '../../interfaces/login';
import { LoginService } from '../../services/login.service';
import { Router } from "@angular/router"

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  login?: Login;
  username: string = "";
  password: string = "";

  constructor(
    private loginService: LoginService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.refreshLogin();
  }

  refreshLogin() {
    this.loginService
      .getLogin()
      .subscribe(
        (login: Login) => {
          this.login = login;
          if (login.complete) this.router.navigate(['/admin']);
        }
      )
  }

  sendLogin() {
    this.loginService
      .startLogin(this.username)
      .subscribe(
        (login: Login) => {
          this.login = login;
          if (login.session_id) {
            this.loginService
              .completeLogin(login.session_id, this.password)
              .subscribe(
                (login: Login) => {
                  this.login = login;
                  if (login.complete) this.router.navigate(['/admin']);
                }
              )
          }
        }
      )
  }

}
