import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChallengesPlayerListComponent } from './challenges-player-list.component';

describe('ChallengesPlayerListComponent', () => {
  let component: ChallengesPlayerListComponent;
  let fixture: ComponentFixture<ChallengesPlayerListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ChallengesPlayerListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ChallengesPlayerListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
