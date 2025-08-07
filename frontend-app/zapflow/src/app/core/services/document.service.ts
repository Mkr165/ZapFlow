import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Document, DocumentContent } from '../types/document.types';
import { Observable } from 'rxjs';
import { environment } from "../../../environments/environment"

@Injectable({ providedIn: 'root' })
export class DocumentService {
  private base = environment.apiBase;

  constructor(private http: HttpClient) {}

  listDocuments(params?: any): Observable<Document[]> {
    return this.http.get<Document[]>(`${this.base}/documents/`, { params });
  }

  getDocument(id: number): Observable<Document> {
    return this.http.get<Document>(`${this.base}/documents/${id}/`);
  }

  createDocument(payload: Document): Observable<Document> {
    return this.http.post<Document>(`${this.base}/documents/`, payload);
  }

  updateDocument(id: number, payload: Partial<Document>): Observable<Document> {
    return this.http.patch<Document>(`${this.base}/documents/${id}/`, payload);
  }

  deleteDocument(id: number) {
    return this.http.delete(`${this.base}/documents/${id}/`);
  }

  // conteúdo
  getContent(id: number) {
    return this.http.get<DocumentContent>(`${this.base}/documents/${id}/content/`);
  }

  setContent(id: number, body: DocumentContent) {
    return this.http.put<DocumentContent>(`${this.base}/documents/${id}/content/`, body);
  }

  // ações
  sendToZapSign(id: number, body: { markdown_text?: string; pdf_url?: string } = {}) {
    return this.http.post<Document>(`${this.base}/documents/${id}/send_to_zapsign/`, body);
  }

  getStatus(id: number) {
    return this.http.get(`${this.base}/documents/${id}/status/`);
  }

  analyze(id: number, text: string) {
    return this.http.post(`${this.base}/documents/${id}/analysis/`, { text });
  }
}
