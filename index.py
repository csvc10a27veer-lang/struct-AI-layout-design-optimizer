import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib.animation as animation
import numpy as np
from matplotlib.widgets import Slider, Button, RadioButtons
import tkinter as tk
from tkinter import ttk
import json
from datetime import datetime

class AdvancedFloorPlanner:
    def __init__(self, total_area_sqft=2000, bhk=3, floors=1):
        self.total_area_sqft = total_area_sqft
        self.bhk = bhk
        self.floors = floors
        self.total_area_sqm = total_area_sqft * 0.092903
        
        # Enhanced room sizes with minimum constraints
        self.room_sizes = {
            'master_bedroom': 18.0, 'bedroom': 12.0, 'living_room': 25.0,
            'kitchen': 10.0, 'dining': 15.0, 'pooja': 2.5, 'utility': 4.0,
            'master_bath': 6.0, 'bathroom': 4.0, 'powder_room': 2.5,
            'balcony': 5.0, 'corridor': 8.0, 'staircase': 10.0
        }
        
        # Areas calculation
        self.wall_thickness = 0.20
        self.total_builtup_area = self.calculate_builtup_area()
        self.carpet_area = self.calculate_carpet_area()
        
        self.layout_params = {
            'margin': 1.5, 'aspect_ratio': 1.6, 'animation_speed': 50
        }
        
        self.width, self.height = self.calculate_dimensions()
        self.fig, self.ax = None, None
        
    def calculate_builtup_area(self):
        """Calculate total built-up area (30% more than carpet)"""
        return self.total_area_sqm * 1.30 * self.floors
    
    def calculate_carpet_area(self):
        """Calculate carpet area (75% of total area)"""
        return self.total_area_sqm * 0.75 * self.floors
    
    def calculate_dimensions(self):
        aspect = self.layout_params['aspect_ratio']
        area = self.total_area_sqm
        w = np.sqrt(area * aspect)
        h = area / w
        return w + 2*self.layout_params['margin'], h + 2*self.layout_params['margin']
    
    def adjust_room_sizes(self, **kwargs):
        """Smart auto-adjustment with constraints"""
        total_custom = sum(kwargs.values())
        remaining = self.total_area_sqm - total_custom
        
        # Minimum sizes constraint
        min_sizes = {'bedroom': 9, 'living_room': 18, 'kitchen': 7}
        
        default_total = sum(self.room_sizes.values())
        for room, size in kwargs.items():
            default_total -= self.room_sizes[room]
        
        scale = max(0.7, remaining / default_total)  # Minimum 70% scale
        
        for room, size in kwargs.items():
            self.room_sizes[room] = max(min_sizes.get(room, 2), size)
        
        for room in self.room_sizes:
            if room not in kwargs:
                self.room_sizes[room] *= scale
    
    def generate_smart_layout(self):
        """Advanced layout algorithm with proper spacing"""
        layout = []
        x, y = self.layout_params['margin'], self.layout_params['margin']
        
        # Main living area (center bottom)
        living_w = np.sqrt(self.room_sizes['living_room'] * 1.3)
        living_h = self.room_sizes['living_room'] / living_w
        layout.append(('Living\nRoom', x+1.5, y, living_w, living_h))
        
        y += living_h + self.wall_thickness
        
        # Kitchen & Dining (left side)
        kitchen_w = 3.2
        kitchen_h = self.room_sizes['kitchen'] / kitchen_w
        layout.append(('Kitchen', x, y, kitchen_w, kitchen_h))
        
        dining_w = np.sqrt(self.room_sizes['dining'] * 1.1)
        dining_h = self.room_sizes['dining'] / dining_w
        layout.append(('Dining', x + kitchen_w + 0.2, y, dining_w, dining_h))
        
        # Bedrooms (right side grid)
        bed_y = y - 0.2
        for i in range(self.bhk):
            bed_w = np.sqrt(self.room_sizes['bedroom'] * 1.1)
            bed_h = self.room_sizes['bedroom'] / bed_w
            
            bed_x = x + kitchen_w + dining_w + 1.5 + (i%2)*(bed_w+0.2)
            bed_y_pos = bed_y if i < 2 else bed_y + bed_h + 0.5
            
            room_name = 'Master BR' if i == 0 else f'BR {i+1}'
            layout.append((room_name, bed_x, bed_y_pos, bed_w, bed_h))
        
        # Bathrooms
        bath_y = y + kitchen_h + 0.3
        for i in range(min(self.bhk, 3)):
            bath_w = 2.2
            bath_h = self.room_sizes['bathroom'] / bath_w
            bath_x = x + kitchen_w + dining_w + 1.5 + i*(2.5)
            layout.append((f'Bath {i+1}', bath_x, bath_y, bath_w, bath_h))
        
        # Additional rooms
        layout.append(('Balcony', self.width-4.5, y+1, 4, 2.5))
        layout.append(('Pooja', self.width-3, self.margin+1, 2.5, 1.8))
        layout.append(('Stairs', self.width-3.5, self.height-4, 3, 3.5))
        
        return layout
    
    def create_interactive_plot(self):
        """Create main interactive plot with sliders"""
        self.fig, self.ax = plt.subplots(1, 1, figsize=(18, 14))
        self.fig.suptitle('🏗️ ADVANCED INTERACTIVE FLOOR PLANNER', fontsize=20, fontweight='bold')
        
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.2, linestyle='--')
        
        # Initial layout
        self.update_layout()
        
        # Add sliders
        ax_area = plt.axes([0.02, 0.02, 0.25, 0.03])
        self.slider_area = Slider(ax_area, 'Total Area\n(sqft)', 800, 5000, 
                                valinit=self.total_area_sqft, valfmt='%d')
        
        ax_bhk = plt.axes([0.3, 0.02, 0.15, 0.03])
        self.slider_bhk = Slider(ax_bhk, 'BHK', 1, 6, valinit=self.bhk, valfmt='%d')
        
        ax_floors = plt.axes([0.48, 0.02, 0.15, 0.03])
        self.slider_floors = Slider(ax_floors, 'Floors', 1, 5, valinit=self.floors, valfmt='%d')
        
        # Connect sliders
        self.slider_area.on_changed(self.update_area)
        self.slider_bhk.on_changed(self.update_bhk)
        self.slider_floors.on_changed(self.update_floors)
        
        # Buttons
        ax_reset = plt.axes([0.75, 0.02, 0.08, 0.04])
        btn_reset = Button(ax_reset, 'Reset')
        btn_reset.on_clicked(self.reset_layout)
        
        ax_animate = plt.axes([0.85, 0.02, 0.08, 0.04])
        btn_animate = Button(ax_animate, 'Animate')
        btn_animate.on_clicked(self.start_animation)
        
        plt.tight_layout()
        plt.show()
    
    def update_layout(self):
        """Update floor plan display"""
        if self.ax is None:
            return
            
        self.ax.clear()
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.2)
        
        # Draw boundary
        outer = FancyBboxPatch((0, 0), self.width, self.height, 
                             boxstyle="round,pad=0.1", linewidth=4, 
                             edgecolor='darkblue', facecolor='none')
        self.ax.add_patch(outer)
        
        # Rooms
        layout = self.generate_smart_layout()
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(layout)))
        
        for i, (name, x, y, w, h) in enumerate(layout):
            room = Rectangle((x, y), w, h, linewidth=2.5, 
                           edgecolor='navy', facecolor=colors[i], alpha=0.75)
            self.ax.add_patch(room)
            
            # Labels
            self.ax.text(x+w/2, y+h/2, name, ha='center', va='center', 
                        fontsize=11, fontweight='bold', color='white')
            
            # Dimensions
            area = w*h
            sqft = area / 0.092903
            self.ax.text(x+w/2, y-h*0.1, f'{w:.1f}×{h:.1f}m\n({sqft:.0f}sf)', 
                        ha='center', va='top', fontsize=8, fontweight='bold')
        
        # Area info box
        builtup = self.total_builtup_area
        carpet = self.carpet_area
        info_text = f"""
🏠 FLOOR PLAN INFO
Total Carpet: {carpet:.0f} sqm ({self.total_area_sqft:.0f} sqft)
Built-up Area: {builtup:.0f} sqm ({builtup/0.092903:.0f} sqft)
BHK: {self.bhk} | Floors: {self.floors}
Rooms: {len(layout)} | Scale: 1:{self.layout_params['aspect_ratio']:.1f}
        """
        self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes, 
                    fontsize=11, fontweight='bold', verticalalignment='top',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow', alpha=0.9))
        
        self.fig.canvas.draw()
    
    def update_area(self, val):
        self.total_area_sqft = val
        self.total_area_sqm = val * 0.092903
        self.total_builtup_area = self.calculate_builtup_area()
        self.carpet_area = self.calculate_carpet_area()
        self.width, self.height = self.calculate_dimensions()
        self.update_layout()
    
    def update_bhk(self, val):
        self.bhk = int(val)
        self.update_layout()
    
    def update_floors(self, val):
        self.floors = int(val)
        self.total_builtup_area = self.calculate_builtup_area()
        self.carpet_area = self.calculate_carpet_area()
        self.update_layout()
    
    def reset_layout(self, event):
        self.total_area_sqft = 2000
        self.bhk = 3
        self.floors = 1
        self.slider_area.reset()
        self.slider_bhk.reset()
        self.slider_floors.reset()
    
    def start_animation(self, event):
        """Animated room building sequence"""
        def animate(frame):
            self.ax.clear()
            layout = self.generate_smart_layout()
            
            # Animate room by room
            for i in range(min(frame//10, len(layout))):
                name, x, y, w, h = layout[i]
                color = plt.cm.Set3(i/len(layout))
                room = Rectangle((x, y), w, h, linewidth=2, 
                               edgecolor='black', facecolor=color, alpha=0.7)
                self.ax.add_patch(room)
                self.ax.text(x+w/2, y+h/2, name.replace('_','\n'), 
                           ha='center', va='center', fontweight='bold')
            
            self.ax.set_xlim(0, self.width)
            self.ax.set_ylim(0, self.height)
            self.ax.set_aspect('equal')
            
        ani = animation.FuncAnimation(self.fig, animate, frames=100, 
                                    interval=self.layout_params['animation_speed'], 
                                    repeat=True)
        plt.pause(0.01)
    
    def export_design(self, filename=None):
        """Export design as image and JSON"""
        if filename is None:
            filename = f"floorplan_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        self.update_layout()
        plt.savefig(f"{filename}.png", dpi=400, bbox_inches='tight')
        plt.savefig(f"{filename}.svg", format='svg', bbox_inches='tight')
        
        # Save JSON data
        data = {
            'timestamp': datetime.now().isoformat(),
            'total_area_sqft': self.total_area_sqft,
            'bhk': self.bhk,
            'floors': self.floors,
            'room_sizes': self.room_sizes,
            'builtup_area_sqm': self.total_builtup_area,
            'carpet_area_sqm': self.carpet_area
        }
        with open(f"{filename}.json", 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Design exported: {filename}.png, .svg, .json")

# Manual Design Mode with Tkinter
class ManualDesigner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏗️ Manual Floor Designer")
        self.root.geometry("1200x800")
        
        self.canvas = None
        self.designer = None
        self.setup_ui()
    
    def setup_ui(self):
        # Control panel
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(control_frame, text="Load Advanced Planner", 
                  command=self.load_advanced).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Export Design", 
                  command=self.export_design).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Animate Build", 
                  command=self.animate_build).pack(side='left', padx=5)
        
        # Canvas for manual drawing
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.canvas = self.fig.canvas
        self.canvas.mpl_connect('button_press_event', self.on_click)
        
        # Embed matplotlib in tkinter
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self.canvas_tk = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas_tk.get_tk_widget().pack(fill='both', expand=True)
    
    def load_advanced(self):
        self.designer = AdvancedFloorPlanner(2200, 3, 2)
        self.designer.fig = self.fig
        self.designer.ax = self.ax
        self.designer.update_layout()
        self.canvas_tk.draw()
    
    def on_click(self, event):
        if self.designer and event.inaxes:
            # Add custom room on click
            x, y = event.xdata, event.ydata
            w, h = 3.0, 2.5
            self.ax.add_patch(Rectangle((x, y), w, h, facecolor='orange', alpha=0.6))
            self.ax.text(x+w/2, y+h/2, 'Custom', ha='center', va='center')
            self.canvas_tk.draw()
    
    def export_design(self):
        if self.designer:
            self.designer.export_design()
    
    def animate_build(self):
        if self.designer:
            self.designer.start_animation(None)
    
    def run(self):
        self.root.mainloop()

# 🚀 MAIN EXECUTION
if __name__ == "__main__":
    print("🏠 ADVANCED FLOOR PLANNER - Choose Mode:")
    print("1. Interactive Sliders (Recommended)")
    print("2. Manual Design Mode")
    print("3. Animation Demo")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        planner = AdvancedFloorPlanner(2500, 3, 2)
        planner.create_interactive_plot()
    
    elif choice == '2':
        designer = ManualDesigner()
        designer.run()
    
    elif choice == '3':
        # Animation demo
        planner = AdvancedFloorPlanner(2000, 3, 1)
        planner.create_interactive_plot()
        plt.show()
    
    else:
        # Quick demo
        print("🎉 Quick Demo - 3BHK 2200 sqft, 2 Floors")
        demo = AdvancedFloorPlanner(2200, 3, 2)
        demo.adjust_room_sizes(living_room=32, kitchen=14, master_bedroom=22)
        demo.create_interactive_plot()