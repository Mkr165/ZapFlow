import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { DocumentsRoutingModule } from './documents-routing.module';
import { DocumentsComponent } from './documents.component';
import { DocumentListComponent } from './pages/document-list/document-list.component';
import { DocumentFormComponent } from './pages/document-form/document-form.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from 'src/app/shared/material/material.module';
import { AnalysisDialogComponent } from './components/analysis-dialog/analysis-dialog.component';


@NgModule({
  declarations: [
    DocumentsComponent,
    DocumentListComponent,
    DocumentFormComponent,
    AnalysisDialogComponent
  ],
  imports: [
    CommonModule,
    DocumentsRoutingModule,
    ReactiveFormsModule,
    FormsModule,
    MaterialModule
  ]
})
export class DocumentsModule { }
