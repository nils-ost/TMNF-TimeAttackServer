import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlayersChallengeListComponent } from './players-challenge-list.component';

describe('PlayersChallengeListComponent', () => {
  let component: PlayersChallengeListComponent;
  let fixture: ComponentFixture<PlayersChallengeListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PlayersChallengeListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PlayersChallengeListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
