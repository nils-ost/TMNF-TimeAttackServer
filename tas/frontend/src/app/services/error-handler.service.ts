import { HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class ErrorHandlerService {
  public errorStatus: number = 0;
  public elementError: boolean = false;
  public elementErrors: any;

  constructor(private router: Router) { }

  public handleError = (error: HttpErrorResponse) => {
    if (error.status === 401) {
      this.handle401Error(error)
    }
    else {
      this.handleOtherError(error);
    }
  }

  private handle401Error = (error: HttpErrorResponse) => {
    this.createErrorMessage(error);
    this.router.navigate(['/login']);
  }

  private handleOtherError = (error: HttpErrorResponse) => {
    this.createErrorMessage(error);
  }

  private createErrorMessage = (error: HttpErrorResponse) => {
    if (error.error) {
      if (error.status === 400 && error.error.errors) {
        this.elementError = true;
        this.elementErrors = error.error.errors;
      } else if (error.status === 400 && error.error.error) {
        this.elementError = true;
        this.elementErrors = error.error.error;
      } else this.elementError = false;
    } else {
      this.elementError = false;
    }
    this.errorStatus = error.status;
    console.error(`Backend returned code ${error.status}, body was: `, error.error);
  }
}
