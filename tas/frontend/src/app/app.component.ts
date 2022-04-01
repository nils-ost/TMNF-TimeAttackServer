import { Component, OnInit } from '@angular/core';
import { PrimeNGConfig } from 'primeng/api';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'TMNF-TimeAttackServer';

  constructor(private primengConfig: PrimeNGConfig) {}

  ngOnInit() {
    this.primengConfig.ripple = true;
    window.addEventListener("keyup", disableF5);
    window.addEventListener("keydown", disableF5);

    function disableF5(e: any) {
      if ((e.which || e.keyCode) == 116) e.preventDefault();
    }
  }
}
