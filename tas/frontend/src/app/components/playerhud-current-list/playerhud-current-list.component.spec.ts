import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlayerhudCurrentListComponent } from './playerhud-current-list.component';

describe('PlayerhudCurrentListComponent', () => {
  let component: PlayerhudCurrentListComponent;
  let fixture: ComponentFixture<PlayerhudCurrentListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PlayerhudCurrentListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PlayerhudCurrentListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
