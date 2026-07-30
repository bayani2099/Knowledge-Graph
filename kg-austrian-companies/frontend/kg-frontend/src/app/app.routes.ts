import { Routes } from '@angular/router';
import { CompanyList } from './pages/company-list/company-list';
import { CompanyDetail } from './pages/company-detail/company-detail';
import { GraphView } from './pages/graph-view/graph-view';

export const routes: Routes = [
  { path: '', component: CompanyList },
  { path: 'company/:id', component: CompanyDetail },
  { path: 'graph', component: GraphView },
  { path: '**', redirectTo: '' }
];