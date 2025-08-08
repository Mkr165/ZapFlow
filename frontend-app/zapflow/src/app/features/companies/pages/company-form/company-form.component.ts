import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CompanyService } from '../../../../core/services/company.service';
import { Company } from '@core/types/company.types';


@Component({
  selector: 'app-company-form',
  templateUrl: './company-form.component.html',
})
export class CompanyFormComponent implements OnInit {
  id?: number;
  loading = false;
  saving = false;

  form = this.fb.group({
    name: ['', Validators.required],
    api_token: ['', Validators.required],
  });

  constructor(
    private fb: FormBuilder,
    private api: CompanyService,
    private route: ActivatedRoute,
    private router: Router,
    private snack: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.id = Number(this.route.snapshot.paramMap.get('id')) || undefined;
    if (this.id) {
      this.loading = true;
      this.api.get(this.id).subscribe({
        next: (c) => {
          this.form.patchValue(c);
          this.loading = false;
        },
        error: (_) => {
          this.loading = false;
          this.snack.open('Falha ao carregar', 'OK', { duration: 2000 });
        },
      });
    }
  }

  save() {
    if (this.form.invalid) return;
    this.saving = true;
    const payload = this.form.value as Company;

    const finalize = () => {
      this.saving = false;
      this.router.navigate(['/companies']);
    };

    if (this.id) {
      this.api.update(this.id, payload).subscribe({
        next: (_) => {
          this.snack.open('Empresa atualizada', 'OK', { duration: 1600 });
          finalize();
        },
        error: (_) => {
          this.snack.open('Falha ao salvar', 'OK', { duration: 2200 });
          this.saving = false;
        },
      });
    } else {
      this.api.create(payload).subscribe({
        next: (_) => {
          this.snack.open('Empresa criada', 'OK', { duration: 1600 });
          finalize();
        },
        error: (_) => {
          this.snack.open('Falha ao criar', 'OK', { duration: 2200 });
          this.saving = false;
        },
      });
    }
  }

  cancel() {
    this.router.navigate(['/companies']);
  }
}
