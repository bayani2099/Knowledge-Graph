import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { KgData } from '../models/kg.model';

@Injectable({
  providedIn: 'root'
})
export class KgService {
  private dataUrl = 'assets/kg-data.json';

  constructor(private http: HttpClient) {}

  getKgData(): Observable<KgData> {
    return this.http.get<KgData>(this.dataUrl);
  }
}