import { TestBed } from '@angular/core/testing';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { AnalysisDialogComponent } from './analysis-dialog.component';
import { MaterialModule } from 'src/app/shared/material/material.module';

describe('AnalysisDialogComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AnalysisDialogComponent],
      providers: [
        { provide: MAT_DIALOG_DATA, useValue: { any: 'data' } },
        { provide: MatDialogRef, useValue: { close: jest.fn() } },
      ],
      imports:[ MaterialModule,]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(AnalysisDialogComponent);
    const comp = fixture.componentInstance;
    expect(comp).toBeTruthy();
  });
});
