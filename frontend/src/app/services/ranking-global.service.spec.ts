import { TestBed } from '@angular/core/testing';

import { RankingGlobalService } from './ranking-global.service';

describe('RankingGlobalService', () => {
  let service: RankingGlobalService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RankingGlobalService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
