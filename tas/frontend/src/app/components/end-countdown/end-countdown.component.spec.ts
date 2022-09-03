import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EndCountdownComponent } from './end-countdown.component';

describe('EndCountdownComponent', () => {
  let component: EndCountdownComponent;
  let fixture: ComponentFixture<EndCountdownComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EndCountdownComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(EndCountdownComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
