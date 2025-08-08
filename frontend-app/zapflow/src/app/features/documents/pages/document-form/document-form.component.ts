import { Component, OnInit } from '@angular/core';
import { FormArray, FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { switchMap } from 'rxjs/operators';
import { of } from 'rxjs';

import { DocumentService } from '../../../../core/services/document.service';
import { Document, DocumentContent } from '../../../../core/types/document.types';
import { AnalysisDialogComponent } from '../../components/analysis-dialog/analysis-dialog.component';
import { CompanyService } from 'src/app/core/services/company.service';
import { Company } from 'src/app/core/types/company.types';

@Component({
  selector: 'app-document-form',
  templateUrl: './document-form.component.html',
  styleUrls: ['./document-form.component.scss']
})
export class DocumentFormComponent implements OnInit {
  id?: number;
  doc?: Document;        // ← guarda o estado atual (status, etc.)
  loading = false;
  saving = false;
  companies: Company[] = [];
  form = this.fb.group({
    company: [1, Validators.required],
    name: ['', Validators.required],
    created_by: [''],
    external_id: [''],
    signers: this.fb.array([
      this.fb.group({ name: ['', Validators.required], email: ['', Validators.required] })
    ])
  });

  content = this.fb.group({
    content_type: ['markdown' as 'markdown'|'url_pdf', Validators.required],
    markdown_text: ['# Contrato\n\nConteúdo mock.'],
    pdf_url: ['']
  });

  get signers(): FormArray { return this.form.get('signers') as FormArray; }

  constructor(
    private fb: FormBuilder,
    private api: DocumentService,
    private route: ActivatedRoute,
    private router: Router,
    private snack: MatSnackBar,
    private dialog: MatDialog,
    private companiesApi: CompanyService
  ) {}

  ngOnInit(): void {
    this.id = Number(this.route.snapshot.paramMap.get('id')) || undefined;

    this.companiesApi.list().subscribe({
        next: list => this.companies = list
    });

    if (this.id) {
      this.loading = true;
      this.api.getDocument(this.id).pipe(
        switchMap(d => {
          this.doc = d;
          this.form.patchValue({
            company: d.company, name: d.name, created_by: d.created_by, external_id: d.external_id
          });
          this.signers.clear();
          (d.signers || []).forEach(s =>
            this.signers.push(this.fb.group({ name: [s.name, Validators.required], email: [s.email, Validators.required] }))
          );
          return this.api.getContent(this.id!);
        })
      ).subscribe({
        next: c => this.content.patchValue(c as DocumentContent),
        complete: () => this.loading = false,
        error: () => this.loading = false
      });
    }

  }

  addSigner() { this.signers.push(this.fb.group({ name: ['', Validators.required], email: ['', Validators.required] })); }
  removeSigner(i: number) { this.signers.removeAt(i); }

  save() {
    if (this.form.invalid) return;
    this.saving = true;
    const payload = this.form.value as unknown as Document;

    const afterDocSaved = (docId: number) => {
      const c = this.content.value as DocumentContent;
      const isMarkdown = c.content_type === 'markdown' && !!c.markdown_text?.trim();
      const isUrl = c.content_type === 'url_pdf' && !!c.pdf_url?.trim();
      console.log(isMarkdown, isUrl)
      if (isMarkdown || isUrl) {
        this.api.setContent(docId, c).subscribe({
          next: _ => this.snack.open('Conteúdo salvo!', 'OK', { duration: 1600 }),
          complete: () => { this.saving = false; this.router.navigate(['/documents']); },
          error: _ => { this.saving = false; this.snack.open('Falha ao salvar conteúdo', 'OK', { duration: 2500 }); }
        });
      } else {
        this.saving = false;
        this.snack.open('Documento salvo. Defina o conteúdo depois.', 'OK', { duration: 2000 });
        this.router.navigate(['/documents']);
      }
    };

    if (this.id) {
      this.api.updateDocument(this.id, payload).subscribe({
        next: d => { this.doc = d; afterDocSaved(this.id!); },
        error: _ => { this.saving = false; this.snack.open('Erro ao salvar', 'OK', { duration: 2500 }); }
      });
    } else {
      this.api.createDocument(payload).subscribe({
        next: d => { this.doc = d; this.id = d.id!; afterDocSaved(d.id!); },
        error: _ => { this.saving = false; this.snack.open('Erro ao criar', 'OK', { duration: 2500 }); }
      });
    }
  }

  // -------- Botão: Enviar para ZapSign
  sendNow() {
    if (!this.id) { this.snack.open('Salve o documento antes de enviar.', 'OK', { duration: 2200 }); return; }
    if (this.doc && this.doc.status !== 'draft') { this.snack.open('Documento já enviado.', 'OK', { duration: 2000 }); return; }

    this.saving = true;
    const c = this.content.value as DocumentContent;

    // garante que o conteúdo atual foi salvo antes do envio
    const saveContent$ = this.api.setContent(this.id!, c);
    saveContent$.pipe(
      switchMap(() => this.api.sendToZapSign(this.id!))
    ).subscribe({
      next: (d: any) => {
        this.doc = d;
        this.snack.open('Enviado para ZapSign!', 'OK', { duration: 1800 });
      },
      error: (e) => {
        console.error(e);
        this.snack.open('Falha ao enviar', 'OK', { duration: 2500 });
      },
      complete: () => this.saving = false
    });
  }

  // -------- Botão: Analisar (abre dialog)
  analyzeNow() {

    if (!this.id) {
      this.snack.open('Salve o documento antes de analisar.', 'OK', { duration: 2200 }); return;
    }
    // texto para análise: usa markdown se houver, senão o nome
    const c = this.content.value as DocumentContent;
    const text = (c.content_type === 'markdown' ? (c.markdown_text || '') : (this.form.value.name || '')) as string;
    const pdf = (c.content_type === 'url_pdf'? (c.pdf_url || '') : (this.form.value.name || '')) as string;
    const finalcontent = pdf ? pdf : text;
    this.loading = true;
    this.api.analyze(this.id!, finalcontent).subscribe({
      next: (res) => this.dialog.open(AnalysisDialogComponent, { data: res, width: '640px' }),
      complete: () => this.loading = false,
      error: () =>{
        this.loading = false,
        this.snack.open('Falha ao analisar', 'OK', { duration: 2500 })
      }
    });
  }

  cancel() { this.router.navigate(['/documents']); }
}
