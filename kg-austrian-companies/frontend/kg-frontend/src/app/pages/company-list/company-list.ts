import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { KgService } from '../../services/kg.service';
import { KgNode } from '../../models/kg.model';

@Component({
  selector: 'app-company-list',
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './company-list.html',
  styleUrl: './company-list.css'
})
export class CompanyList implements OnInit {
  companies: KgNode[] = [];
  searchText = '';

  constructor(private kgService: KgService) {}

  ngOnInit(): void {
    this.kgService.getKgData().subscribe(data => {
      this.companies = data.nodes;
    });
  }

  get filteredCompanies(): KgNode[] {
    return this.companies.filter(company =>
      company.label.toLowerCase().includes(this.searchText.toLowerCase())
    );
  }
}