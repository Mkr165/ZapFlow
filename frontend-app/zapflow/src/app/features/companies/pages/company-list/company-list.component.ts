import { Component, OnInit, ViewChild } from '@angular/core';
import { CompanyService } from '../../../../core/services/company.service';
import { Company } from '../../../../core/types/company.types';
import { Router } from '@angular/router';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-company-list',
  templateUrl: './company-list.component.html',
})
export class CompanyListComponent implements OnInit {
  cols = ['id', 'name', 'api_token', 'actions'];
  data = new MatTableDataSource<Company>([]);
  loading = false;

  @ViewChild(MatPaginator) paginator!: MatPaginator;

  constructor(
    private api: CompanyService,
    private router: Router,
    private snack: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.fetch();
  }
  ngAfterViewInit() {
    this.data.paginator = this.paginator;
  }

  fetch() {
    this.loading = true;
    this.api.list().subscribe({
      next: (rows) => {
        this.data.data = rows;
        this.loading = false;
      },
      error: (_) => {
        this.loading = false;
        this.snack.open('Falha ao carregar', 'OK', { duration: 2000 });
      },
    });
  }

  copy(token: string) {
    navigator.clipboard.writeText(token);
    this.snack.open('Copiado!', 'OK', { duration: 1200 });
  }

  newCompany() {
    this.router.navigate(['/companies/new']);
  }
  edit(c: Company) {
    this.router.navigate(['/companies', c.id, 'edit']);
  }
  remove(c: Company) {
    if (!confirm(`Excluir empresa "${c.name}"?`)) return;
    this.api.delete(c.id!).subscribe({
      next: (_) => {
        this.snack.open('Excluída', 'OK', { duration: 1500 });
        this.fetch();
      },
      error: (_) =>
        this.snack.open('Falha ao excluir', 'OK', { duration: 2000 }),
    });
  }
}
