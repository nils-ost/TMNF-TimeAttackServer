import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RankingChallengeComponent } from './ranking-challenge.component';

describe('RankingChallengeComponent', () => {
  let component: RankingChallengeComponent;
  let fixture: ComponentFixture<RankingChallengeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RankingChallengeComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RankingChallengeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
