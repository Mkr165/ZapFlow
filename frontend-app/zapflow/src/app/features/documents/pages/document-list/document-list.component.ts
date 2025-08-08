import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { DocumentService } from '../../../../core/services/document.service';
import { Document } from '../../../../core/types/document.types';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-document-list',
  templateUrl: './document-list.component.html',
})
export class DocumentListComponent implements OnInit {
  cols = ['id', 'name', 'status', 'signers', 'actions'];
  data = new MatTableDataSource<Document>([]);
  loading = false;

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private api: DocumentService,
    private router: Router,
    private snack: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.fetch();
  }
  ngAfterViewInit(): void {
    this.data.paginator = this.paginator;
    this.data.sort = this.sort;
  }

  fetch() {
    this.loading = true;
    this.api.listDocuments().subscribe({
      next: (d) => {
        this.data.data = d;
        this.loading = false;
      },
      error: (_) => {
        this.loading = false;
      },
    });
  }

  newDoc() {
    this.router.navigate(['/documents/new']);
  }
  send(d: Document) {
    this.api.sendToZapSign(d.id!).subscribe(() => this.fetch());
  }
  status(d: Document) {
    this.api.getStatus(d.id!).subscribe(()=>this.fetch());
  }
  analyze(d: Document) {
    this.api.analyze(d.id!, d.name).subscribe(console.log);
  }

  remove(c: Document) {
    if (!confirm(`Excluir empresa "${c.name}"?`)) return;
    this.api.deleteDocument(c.id!).subscribe({
      next: (_) => {
        this.snack.open('Excluída', 'OK', { duration: 1500 });
        this.fetch();
      },
      error: (_) =>
        this.snack.open('Falha ao excluir', 'OK', { duration: 2000 }),
    });
  }
}
