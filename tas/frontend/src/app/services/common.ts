import { HttpErrorResponse } from '@angular/common/http';
import { throwError } from 'rxjs';

export function handleError(error: HttpErrorResponse) {
  if (error.status === 0) {
    console.error('An error occurred:', error.error);
  } else {
    console.error(`Backend returned code ${error.status}, body was: `, error.error);
  }
  return throwError(() => new Error('Something bad happened; please try again later.'));
}

export function cleanName(name: string) {
  const colorMarker = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"];
  let cleanedName: string = "";
  let remove: number = 0;
  let wasEsc: boolean = false;
  for (let i = 0; i < name.length; i++) {
    if (!wasEsc && remove == 0 && name[i] != "$") cleanedName += name[i];
    else if (wasEsc && name[i] == "$") {
      cleanedName += "$";
      wasEsc = false;
    }
    else if (!wasEsc && name[i] == "$") wasEsc = true;
    else if (wasEsc && colorMarker.includes(name[i].toLowerCase())) {
      wasEsc = false;
      remove = 2;
    }
    else if (wasEsc) wasEsc = false;
    else if (remove > 0) remove -= 1;
  }
  return cleanedName;
}
