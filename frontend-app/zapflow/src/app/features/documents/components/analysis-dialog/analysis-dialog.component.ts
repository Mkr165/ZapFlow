import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-analysis-dialog',
  templateUrl: './analysis-dialog.component.html'
})
export class AnalysisDialogComponent {
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: any,
    private ref: MatDialogRef<AnalysisDialogComponent>
  ) {}
  close() { this.ref.close(); }
}
