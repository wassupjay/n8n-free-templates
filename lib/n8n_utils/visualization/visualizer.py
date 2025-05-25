"""
n8n Workflow Visualizer

This module provides functionality to visualize n8n workflows as graphs.
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import BoxStyle, FancyBboxPatch

class WorkflowVisualizer:
    """Class for visualizing n8n workflows."""
    
    def __init__(self, workflow_data: Dict):
        """Initialize with workflow data."""
        self.workflow = workflow_data
        self.graph = nx.DiGraph()
        self.pos = {}
        self.node_colors = []
        self.node_sizes = []
        
        # Color mapping for different node types
        self.type_colors = {
            'n8n-nodes-base.start': '#ff9a9c',
            'n8n-nodes-base.httpRequest': '#a4c2f4',
            'n8n-nodes-base.if': '#ffcc80',
            'n8n-nodes-base.function': '#d5a6bd',
            'n8n-nodes-base.set': '#b4a7d6',
            'n8n-nodes-base.code': '#a2c4c9',
            'n8n-nodes-base.moveBinaryData': '#b6d7a8',
            'n8n-nodes-base.spreadsheetFile': '#f9cb9c',
            'n8n-nodes-base.switch': '#ea9999',
            'n8n-nodes-base.merge': '#9fc5e8',
            'n8n-nodes-base.noOp': '#cccccc',
        }
    
    def parse_workflow(self):
        """Parse the workflow data and build the graph."""
        # Add nodes
        for node in self.workflow.get('nodes', []):
            node_id = node['id']
            node_type = node['type']
            node_name = node.get('name', node_type.split('.')[-1])
            
            # Add node to graph
            self.graph.add_node(node_id, 
                             label=node_name, 
                             type=node_type,
                             parameters=node.get('parameters', {}))
            
            # Store position if available
            if 'position' in node and len(node['position']) >= 2:
                self.pos[node_id] = (node['position'][0], -node['position'][1])  # Invert y for visualization
        
        # Add edges based on connections
        connections = self.workflow.get('connections', {})
        for source_node_id, source_connections in connections.items():
            for connection_type, connection_list in source_connections.items():
                for connection in connection_list:
                    target_node_id = connection['node']
                    self.graph.add_edge(source_node_id, target_node_id, 
                                      connection_type=connection_type)
    
    def _get_node_color(self, node_type: str) -> str:
        """Get color for a node based on its type."""
        return self.type_colors.get(node_type, '#cccccc')
    
    def _get_node_label(self, node_data: Dict) -> str:
        """Generate a label for a node."""
        label = node_data.get('label', '')
        # Truncate long labels
        if len(label) > 20:
            return f"{label[:18]}..."
        return label
    
    def draw(self, output_file: Optional[str] = None, show: bool = True):
        """Draw the workflow graph.
        
        Args:
            output_file: If provided, save the figure to this file
            show: If True, display the figure
        """
        if not self.pos:
            # If no positions are defined, use a layout algorithm
            self.pos = nx.spring_layout(self.graph, k=0.5, iterations=50)
        
        plt.figure(figsize=(16, 12))
        
        # Draw edges first (behind nodes)
        nx.draw_networkx_edges(
            self.graph, 
            self.pos, 
            edge_color='#888888',
            arrows=True,
            arrowstyle='-|>',
            arrowsize=15,
            node_size=2000,
            width=1.5,
            connectionstyle="arc3,rad=0.1"
        )
        
        # Draw nodes with colors based on type
        for node_id, node_data in self.graph.nodes(data=True):
            node_type = node_data.get('type', 'unknown')
            color = self._get_node_color(node_type)
            
            # Draw node
            nx.draw_networkx_nodes(
                self.graph, 
                self.pos, 
                nodelist=[node_id],
                node_color=color,
                node_size=2000,
                edgecolors='#333333',
                linewidths=1,
                alpha=0.9
            )
            
            # Add node type as a small label below the node
            plt.text(
                self.pos[node_id][0], 
                self.pos[node_id][1] - 0.07, 
                node_type.split('.')[-1], 
                fontsize=6, 
                ha='center',
                va='top',
                color='#555555'
            )
        
        # Draw node labels
        labels = {n: d['label'] for n, d in self.graph.nodes(data=True)}
        nx.draw_networkx_labels(
            self.graph, 
            self.pos, 
            labels=labels,
            font_size=8,
            font_weight='bold',
            font_color='#000000',
            font_family='sans-serif'
        )
        
        # Add edge labels (connection types)
        edge_labels = {(u, v): d.get('connection_type', '') 
                      for u, v, d in self.graph.edges(data=True)}
        nx.draw_networkx_edge_labels(
            self.graph, 
            self.pos, 
            edge_labels=edge_labels,
            font_size=7,
            font_color='#666666',
            label_pos=0.5
        )
        
        plt.title(f"Workflow: {self.workflow.get('name', 'Untitled')}", fontsize=14)
        plt.axis('off')
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=150, bbox_inches='tight')
            print(f"Workflow visualization saved to {output_file}")
        
        if show:
            plt.show()
        else:
            plt.close()

def visualize_workflow(workflow_data: Dict, output_file: Optional[str] = None, show: bool = True):
    """Visualize an n8n workflow.
    
    Args:
        workflow_data: The workflow data as a dictionary
        output_file: If provided, save the visualization to this file
        show: If True, display the visualization
    """
    visualizer = WorkflowVisualizer(workflow_data)
    visualizer.parse_workflow()
    visualizer.draw(output_file=output_file, show=show)

def visualize_workflow_file(workflow_file: Union[str, Path], output_file: Optional[str] = None, show: bool = True):
    """Visualize an n8n workflow from a JSON file.
    
    Args:
        workflow_file: Path to the workflow JSON file
        output_file: If provided, save the visualization to this file
        show: If True, display the visualization
    """
    with open(workflow_file, 'r', encoding='utf-8') as f:
        workflow_data = json.load(f)
    
    if not output_file and not show:
        base_name = os.path.splitext(os.path.basename(workflow_file))[0]
        output_file = f"{base_name}_visualization.png"
    
    visualize_workflow(workflow_data, output_file=output_file, show=show)

def main():
    """Command-line interface for the visualizer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualize n8n workflows.')
    parser.add_argument('workflow_file', help='Path to the n8n workflow JSON file')
    parser.add_argument('-o', '--output', help='Output file path for the visualization')
    parser.add_argument('--no-show', action='store_true', help='Do not display the visualization')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.workflow_file):
        print(f"Error: File '{args.workflow_file}' not found")
        sys.exit(1)
    
    try:
        visualize_workflow_file(
            args.workflow_file, 
            output_file=args.output,
            show=not args.no_show
        )
    except Exception as e:
        print(f"Error visualizing workflow: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
