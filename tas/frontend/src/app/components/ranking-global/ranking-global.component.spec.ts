import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RankingGlobalComponent } from './ranking-global.component';

describe('RankingGlobalComponent', () => {
  let component: RankingGlobalComponent;
  let fixture: ComponentFixture<RankingGlobalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RankingGlobalComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RankingGlobalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
