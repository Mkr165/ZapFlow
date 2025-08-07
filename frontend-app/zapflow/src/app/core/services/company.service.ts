import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Observable } from 'rxjs';
import { Company } from '../types/company.types';

@Injectable({ providedIn: 'root' })
export class CompanyService {
  private base = environment.apiBase;
  constructor(private http: HttpClient) {}

  list(): Observable<Company[]> {
    return this.http.get<Company[]>(`${this.base}/companies/`);
  }
  get(id: number): Observable<Company> {
    return this.http.get<Company>(`${this.base}/companies/${id}/`);
  }
  create(payload: Company): Observable<Company> {
    return this.http.post<Company>(`${this.base}/companies/`, payload);
  }
  update(id: number, payload: Partial<Company>): Observable<Company> {
    return this.http.patch<Company>(`${this.base}/companies/${id}/`, payload);
  }
  delete(id: number) {
    return this.http.delete(`${this.base}/companies/${id}/`);
  }
}
