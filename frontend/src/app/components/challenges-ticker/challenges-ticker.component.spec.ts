import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChallengesTickerComponent } from './challenges-ticker.component';

describe('ChallengesTickerComponent', () => {
  let component: ChallengesTickerComponent;
  let fixture: ComponentFixture<ChallengesTickerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ChallengesTickerComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ChallengesTickerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
