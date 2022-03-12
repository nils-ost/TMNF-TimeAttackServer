import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlayersLaptimeListComponent } from './players-laptime-list.component';

describe('PlayersLaptimeListComponent', () => {
  let component: PlayersLaptimeListComponent;
  let fixture: ComponentFixture<PlayersLaptimeListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PlayersLaptimeListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PlayersLaptimeListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
