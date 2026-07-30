export interface KgNode {
  id: string;
  label: string;
  type: string;
}

export interface KgEdge {
  from: string;
  to: string;
  label: string;
  type: string;
  percentage: number;
}

export interface ControlRelation {
  controller: string;
  controlled: string;
  type: string;
  path: string[];
  reason: string;
}

export interface KgData {
  nodes: KgNode[];
  edges: KgEdge[];
  direct_control: ControlRelation[];
  indirect_control: ControlRelation[];
}