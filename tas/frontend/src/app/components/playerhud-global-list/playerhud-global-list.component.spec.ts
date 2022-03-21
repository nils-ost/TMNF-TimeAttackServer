import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlayerhudGlobalListComponent } from './playerhud-global-list.component';

describe('PlayerhudGlobalListComponent', () => {
  let component: PlayerhudGlobalListComponent;
  let fixture: ComponentFixture<PlayerhudGlobalListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PlayerhudGlobalListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PlayerhudGlobalListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
