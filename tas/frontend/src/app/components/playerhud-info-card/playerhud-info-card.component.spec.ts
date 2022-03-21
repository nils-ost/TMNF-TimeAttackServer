import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlayerhudInfoCardComponent } from './playerhud-info-card.component';

describe('PlayerhudInfoCardComponent', () => {
  let component: PlayerhudInfoCardComponent;
  let fixture: ComponentFixture<PlayerhudInfoCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PlayerhudInfoCardComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PlayerhudInfoCardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
