export interface Signer {
  id?: number;
  token?: string;
  status?: 'pending'|'signed'|'rejected';
  name: string;
  email: string;
  external_id?: string;
}

export interface Document {
  id?: number;
  company: number;
  name: string;
  created_by?: string;
  external_id?: string;
  status?: 'draft'|'sent'|'signed'|'canceled';
  open_id?: number|null;
  token?: string;
  created_at?: string;
  last_updated_at?: string;
  signers: Signer[];
}

export interface DocumentContent {
  content_type: 'markdown'|'url_pdf';
  markdown_text?: string;
  pdf_url?: string;
}
