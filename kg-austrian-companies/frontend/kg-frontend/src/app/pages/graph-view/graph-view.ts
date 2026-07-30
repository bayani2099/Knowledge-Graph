import { Component, ElementRef, AfterViewInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';

import { Network } from 'vis-network/standalone';
import { KgService } from '../../services/kg.service';

@Component({
  selector: 'app-graph-view',
  imports: [CommonModule],
  templateUrl: './graph-view.html',
  styleUrl: './graph-view.css'
})
export class GraphView implements AfterViewInit {
  @ViewChild('networkContainer')
  networkContainer!: ElementRef;

  constructor(private kgService: KgService) {}

  ngAfterViewInit(): void {
    this.kgService.getKgData().subscribe(data => {
      console.log('KG DATA LOADED:', data);

      const nodes = data.nodes.map(node => ({
        id: node.id,
        label: node.label,
        shape: 'box',
        color:
          node.type === 'company'
            ? '#60a5fa'
            : '#86efac'
      }));

      const edges = data.edges.map(edge => ({
        from: edge.from,
        to: edge.to,
        label: `${edge.percentage}%`,
        arrows: 'to',
        title: `${edge.from} owns ${edge.percentage}% of ${edge.to}`
      }));

      const graphData = {
        nodes,
        edges
      };

      const options = {
        autoResize: true,
        height: '700px',
        width: '100%',
        nodes: {
          shape: 'box',
          margin: {
            top: 10,
            right: 10,
            bottom: 10,
            left: 10
          },
          font: {
            size: 14
          }
        },
        edges: {
          arrows: {
            to: {
              enabled: true
            }
          },
          font: {
            size: 12,
            align: 'middle'
          },
          smooth: {
            enabled: true,
            type: 'dynamic',
            roundness: 0.5
          }
        },
        physics: {
          enabled: false
        },
        interaction: {
          dragNodes: true,
          dragView: true,
          zoomView: true,
          hover: true
        }
      };

      new Network(this.networkContainer.nativeElement, graphData, options);
    });
  }
}