import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WallboardComponent } from './wallboard.component';

describe('WallboardComponent', () => {
  let component: WallboardComponent;
  let fixture: ComponentFixture<WallboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ WallboardComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(WallboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
