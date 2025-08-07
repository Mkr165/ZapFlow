import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CompanyListComponent } from './pages/company-list/company-list.component';
import { CompanyFormComponent } from './pages/company-form/company-form.component';

const routes: Routes = [
  { path: '', component: CompanyListComponent },
  { path: 'new', component: CompanyFormComponent },
  { path: ':id/edit', component: CompanyFormComponent },
];

@NgModule({ imports: [RouterModule.forChild(routes)], exports: [RouterModule] })
export class CompaniesRoutingModule {}
