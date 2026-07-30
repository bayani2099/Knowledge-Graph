import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GraphView } from './graph-view';

describe('GraphView', () => {
  let component: GraphView;
  let fixture: ComponentFixture<GraphView>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GraphView],
    }).compileComponents();

    fixture = TestBed.createComponent(GraphView);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
