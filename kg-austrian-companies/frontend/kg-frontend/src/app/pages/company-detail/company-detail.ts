import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { KgService } from '../../services/kg.service';
import { KgData, KgEdge, ControlRelation } from '../../models/kg.model';

@Component({
  selector: 'app-company-detail',
  imports: [CommonModule, RouterLink],
  templateUrl: './company-detail.html',
  styleUrl: './company-detail.css'
})
export class CompanyDetail implements OnInit {
  companyId = '';
  data?: KgData;

  incomingOwnership: KgEdge[] = [];
  outgoingOwnership: KgEdge[] = [];

  directControls: ControlRelation[] = [];
  indirectControls: ControlRelation[] = [];

  controlledByDirect: ControlRelation[] = [];
  controlledByIndirect: ControlRelation[] = [];

  constructor(
    private route: ActivatedRoute,
    private kgService: KgService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.companyId = decodeURIComponent(params.get('id') || '').trim();

      this.kgService.getKgData().subscribe(data => {
        this.data = data;

        this.outgoingOwnership = data.edges.filter(edge =>
          edge.from.trim() === this.companyId
        );

        this.incomingOwnership = data.edges.filter(edge =>
          edge.to.trim() === this.companyId
        );

        this.directControls = data.direct_control.filter(relation =>
          relation.controller.trim() === this.companyId
        );

        this.indirectControls = data.indirect_control.filter(relation =>
          relation.controller.trim() === this.companyId
        );

        this.controlledByDirect = data.direct_control.filter(relation =>
          relation.controlled.trim() === this.companyId
        );

        this.controlledByIndirect = data.indirect_control.filter(relation =>
          relation.controlled.trim() === this.companyId
        );

        this.cdr.detectChanges();
      });
    });
  }
}