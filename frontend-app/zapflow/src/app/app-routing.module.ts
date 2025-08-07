import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  {
    path: 'documents',
    loadChildren: () =>
      import('./features/documents/documents.module').then(
        (m) => m.DocumentsModule
      ),
  },
  { path: 'companies', loadChildren: () => import('./features/companies/companies.module').then(m => m.CompaniesModule) },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
