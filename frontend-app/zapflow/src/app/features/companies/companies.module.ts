import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { CompaniesRoutingModule } from './companies-routing.module';

import { CompanyListComponent } from './pages/company-list/company-list.component';
import { CompanyFormComponent } from './pages/company-form/company-form.component';
import { MaterialModule } from 'src/app/shared/material/material.module';

@NgModule({
  declarations: [CompanyListComponent, CompanyFormComponent],
  imports: [
    CommonModule,
    CompaniesRoutingModule,
    ReactiveFormsModule,
    FormsModule,
    MaterialModule,
  ],
})
export class CompaniesModule {}
