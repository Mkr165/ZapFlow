import { TestBed, fakeAsync, tick } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { of, throwError } from 'rxjs';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';

import { DocumentListComponent } from './document-list.component';
import { DocumentService } from '../../../../core/services/document.service';
import { Document } from '../../../../core/types/document.types';

describe('DocumentListComponent (Jest)', () => {
  let component: DocumentListComponent;
  let api: jest.Mocked<DocumentService>;
  let router: { navigate: jest.Mock };
  let snack: { open: jest.Mock };

  const DOCS: Document[] = [
    { id: 1, name: 'A', status: 'draft', company: 1, signers: [] } as any,
    { id: 2, name: 'B', status: 'sent', company: 1, signers: [] } as any,
  ];

  function create() {
    TestBed.configureTestingModule({
      declarations: [DocumentListComponent],
      providers: [
        { provide: DocumentService, useValue: api },
        { provide: Router, useValue: router },
        { provide: MatSnackBar, useValue: snack },
      ],

      schemas: [NO_ERRORS_SCHEMA],
    }).compileComponents();

    const fixture = TestBed.createComponent(DocumentListComponent);
    component = fixture.componentInstance;
    return { fixture };
  }

  beforeEach(() => {
    api = {
      listDocuments: jest.fn(),
      sendToZapSign: jest.fn(),
      getStatus: jest.fn(),
      analyze: jest.fn(),
      deleteDocument: jest.fn(),
    } as any;

    router = { navigate: jest.fn() };
    snack  = { open: jest.fn() };
  });

  it('ngOnInit → chama fetch e popula a tabela', fakeAsync(() => {
    api.listDocuments.mockReturnValue(of(DOCS)); // define retorno ANTES de create()
    const { fixture } = create();

    fixture.detectChanges();           // dispara ngOnInit -> fetch()


    tick();
    expect(api.listDocuments).toHaveBeenCalledTimes(1);
    expect(component.data.data).toEqual(DOCS);
    expect(component.loading).toBe(false);
  }));

  it('fetch (erro) → desmarca loading', fakeAsync(() => {
    api.listDocuments.mockReturnValue(throwError(() => new Error('boom')));
    const { fixture } = create();
    fixture.detectChanges();
    tick();
    expect(component.loading).toBe(false);
    expect(component.data.data).toEqual([]);
  }));

  it('ngAfterViewInit → conecta paginator e sort', () => {
    api.listDocuments.mockReturnValue(of([]));
    create();
    (component as any).paginator = {} as MatPaginator;
    (component as any).sort = {} as MatSort;
    component.ngAfterViewInit();
    expect(component.data.paginator).toBe(component.paginator);
    expect(component.data.sort).toBe(component.sort);
  });

  it('newDoc navega para /documents/new', () => {
    api.listDocuments.mockReturnValue(of([]));
    create();
    component.newDoc();
    expect(router.navigate).toHaveBeenCalledWith(['/documents/new']);
  });

  it('send → chama API e depois fetch', fakeAsync(() => {
    api.listDocuments.mockReturnValue(of([]));
    api.sendToZapSign.mockReturnValue(of({ id: 123 } as any)); // 👈 evita erro de tipo
    const { fixture } = create();
    const spyFetch = jest.spyOn(component, 'fetch');
    component.send({ id: 123 } as any);
    tick();
    expect(api.sendToZapSign).toHaveBeenCalledWith(123);
    expect(spyFetch).toHaveBeenCalled();
  }));

  it('status → chama API e depois fetch', fakeAsync(() => {
    api.listDocuments.mockReturnValue(of([]));
    api.getStatus.mockReturnValue(of({ id: 7 } as any));
    const { fixture } = create();
    const spyFetch = jest.spyOn(component, 'fetch');
    component.status({ id: 7 } as any);
    tick();
    expect(api.getStatus).toHaveBeenCalledWith(7);
    expect(spyFetch).toHaveBeenCalled();
  }));

  it('analyze → chama API com id e name', () => {
    api.listDocuments.mockReturnValue(of([]));
    api.analyze.mockReturnValue(of({ score: 0.9 } as any));
    create();
    component.analyze({ id: 9, name: 'Contrato X' } as any);
    expect(api.analyze).toHaveBeenCalledWith(9, 'Contrato X');
  });

  describe('remove', () => {
    let confirmSpy: jest.SpyInstance;

    beforeEach(() => {
      confirmSpy = jest.spyOn(window, 'confirm');
    });

    it('quando usuário cancela → não chama API', () => {
      api.listDocuments.mockReturnValue(of([]));
      create();
      confirmSpy.mockReturnValue(false);
      component.remove({ id: 5, name: 'Emp' } as any);
      expect(api.deleteDocument).not.toHaveBeenCalled();
      expect(snack.open).not.toHaveBeenCalled();
    });

    it('quando confirma (sucesso) → delete + snackbar + fetch', fakeAsync(() => {
      api.listDocuments.mockReturnValue(of([]));
      api.deleteDocument.mockReturnValue(of({}));
      const { fixture } = create();
      const spyFetch = jest.spyOn(component, 'fetch');
      confirmSpy.mockReturnValue(true);
      component.remove({ id: 5, name: 'Emp' } as any);
      tick();
      expect(api.deleteDocument).toHaveBeenCalledWith(5);
      expect(snack.open).toHaveBeenCalledWith('Excluída', 'OK', expect.any(Object));
      expect(spyFetch).toHaveBeenCalled();
    }));

    it('quando confirma (erro) → snackbar erro', fakeAsync(() => {
      api.listDocuments.mockReturnValue(of([]));
      api.deleteDocument.mockReturnValue(throwError(() => new Error('del fail')));
      create();
      confirmSpy.mockReturnValue(true);
      component.remove({ id: 99, name: 'Emp' } as any);
      tick();
      expect(api.deleteDocument).toHaveBeenCalledWith(99);
      expect(snack.open).toHaveBeenCalledWith('Falha ao excluir', 'OK', expect.any(Object));
    }));
  });
});
