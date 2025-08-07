import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DocumentsComponent } from './documents.component';
import { DocumentFormComponent } from './pages/document-form/document-form.component';
import { DocumentListComponent } from './pages/document-list/document-list.component';

//const routes: Routes = [{ path: '', component: DocumentsComponent }];

const routes: Routes = [
  { path: '', component: DocumentListComponent },
  { path: 'new', component: DocumentFormComponent },
  { path: ':id/edit', component: DocumentFormComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class DocumentsRoutingModule {}
