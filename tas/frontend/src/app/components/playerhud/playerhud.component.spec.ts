import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlayerhudComponent } from './playerhud.component';

describe('PlayerhudComponent', () => {
  let component: PlayerhudComponent;
  let fixture: ComponentFixture<PlayerhudComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PlayerhudComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PlayerhudComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
