import { TestBed } from '@angular/core/testing';
import { ReactiveFormsModule, FormArray } from '@angular/forms';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { Router, ActivatedRoute, convertToParamMap } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { of } from 'rxjs';

import { DocumentFormComponent } from './document-form.component';

// ajuste os aliases se necessário
import { DocumentService } from '@core/services/document.service';
import { CompanyService } from '@core/services/company.service';

describe('DocumentFormComponent (Jest)', () => {
  let component: DocumentFormComponent;

  let api: jest.Mocked<DocumentService>;
  let companiesApi: jest.Mocked<CompanyService>;
  let snack: { open: jest.Mock };
  let dialog: { open: jest.Mock };
  let router: Router;

  // ActivatedRoute stub (sem id por padrão)
  let routeStub: { snapshot: { paramMap: any } };

  function setRouteId(id: string | null) {
    routeStub.snapshot.paramMap = convertToParamMap({ id });
  }

  async function create() {
    await TestBed.configureTestingModule({
      imports: [
        ReactiveFormsModule,
        RouterTestingModule.withRoutes([]),
        NoopAnimationsModule,
      ],
      declarations: [DocumentFormComponent],
      providers: [
        { provide: DocumentService, useValue: api },
        { provide: CompanyService, useValue: companiesApi },
        { provide: MatSnackBar, useValue: snack },
        { provide: MatDialog, useValue: dialog },
        { provide: ActivatedRoute, useValue: routeStub },
      ],
      schemas: [NO_ERRORS_SCHEMA], // ignora template/material
    }).compileComponents();

    const fixture = TestBed.createComponent(DocumentFormComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    return { fixture };
  }

  beforeEach(() => {
    api = {
      getDocument: jest.fn(),
      getContent: jest.fn(),
      createDocument: jest.fn(),
      updateDocument: jest.fn(),
      setContent: jest.fn(),
      sendToZapSign: jest.fn(),
      analyze: jest.fn(),
      deleteDocument: jest.fn(),
      listDocuments: jest.fn(),
      getStatus: jest.fn(),
    } as any;

    companiesApi = {
      list: jest.fn(),
    } as any;

    snack = { open: jest.fn() };
    dialog = { open: jest.fn() };

    // rota sem id por padrão
    routeStub = {
      snapshot: {
        paramMap: convertToParamMap({ id: null }),
      },
    };

    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });


  // ---------- add/remove signer ----------
  it('addSigner / removeSigner funcionam', async () => {
    companiesApi.list.mockReturnValue(of([]));
    await create();

    expect((component.signers as FormArray).length).toBe(1);
    component.addSigner();
    expect((component.signers as FormArray).length).toBe(2);
    component.removeSigner(0);
    expect((component.signers as FormArray).length).toBe(1);
  });


  it('sendNow: já enviado (status != draft) → snackbar e não chama API', async () => {
    companiesApi.list.mockReturnValue(of([]));
    await create();

    component.id = 99;
    component.doc = { id: 99, status: 'sent' } as any;

    component.sendNow();

    expect(snack.open).toHaveBeenCalledWith('Documento já enviado.', 'OK', expect.any(Object));
    expect(api.setContent).not.toHaveBeenCalled();
    expect(api.sendToZapSign).not.toHaveBeenCalled();
  });

  it('sendNow: salva conteúdo atual e envia para ZapSign', async () => {
    companiesApi.list.mockReturnValue(of([]));
    await create();

    component.id = 15;
    component.doc = { id: 15, status: 'draft' } as any;

    component.content.patchValue({
      content_type: 'markdown',
      markdown_text: '# atual',
      pdf_url: '',
    });

    api.setContent.mockReturnValue(of({content_type: 'markdown', markdown_text: '# md', pdf_url: ''}));
    api.sendToZapSign.mockReturnValue(of({ id: 15, status: 'sent' } as any));

    component.sendNow();

    expect(api.setContent).toHaveBeenCalledWith(15, component.content.value as any);
    expect(api.sendToZapSign).toHaveBeenCalledWith(15);
    expect(snack.open).toHaveBeenCalledWith('Enviado para ZapSign!', 'OK', expect.any(Object));
    expect(component.doc?.status).toBe('sent');
  });

  // ---------- analyzeNow ----------
  it('analyzeNow: sem id → snackbar e não chama API', async () => {
    companiesApi.list.mockReturnValue(of([]));
    await create();

    component.id = undefined;
    component.analyzeNow();

    expect(snack.open).toHaveBeenCalledWith('Salve o documento antes de analisar.', 'OK', expect.any(Object));
    expect(api.analyze).not.toHaveBeenCalled();
  });

  it('analyzeNow: com id → chama API com texto certo (markdown prioritário)', async () => {
    companiesApi.list.mockReturnValue(of([]));
    await create();

    component.id = 5;
    component.form.patchValue({ name: 'Nome Doc' });
    component.content.patchValue({
      content_type: 'markdown',
      markdown_text: 'Texto MD',
      pdf_url: '',
    });

    api.analyze.mockReturnValue(of({ score: 0.9 } as any));
    dialog.open.mockReturnValue({} as any);

    component.analyzeNow();

    expect(api.analyze).toHaveBeenCalledWith(5, 'Nome Doc');
    expect(dialog.open).toHaveBeenCalled();
  });

  it('analyzeNow: com url_pdf → envia url', async () => {
    companiesApi.list.mockReturnValue(of([]));
    await create();

    component.id = 6;
    component.form.patchValue({ name: 'Nome Doc' });
    component.content.patchValue({
      content_type: 'url_pdf',
      markdown_text: '',
      pdf_url: 'https://pdf.url',
    });

    api.analyze.mockReturnValue(of({ score: 1 } as any));
    dialog.open.mockReturnValue({} as any);

    component.analyzeNow();

    expect(api.analyze).toHaveBeenCalledWith(6, 'https://pdf.url');
  });

  // ---------- cancel ----------
  it('cancel navega para /documents', async () => {
    companiesApi.list.mockReturnValue(of([]));
    await create();

    const navSpy = jest.spyOn(router, 'navigate');
    component.cancel();
    expect(navSpy).toHaveBeenCalledWith(['/documents']);
  });
});
