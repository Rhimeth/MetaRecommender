import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from game_recommender import GameRecommender
import pandas as pd
from tkinter import filedialog
import os
import logging
from datetime import datetime

class MetacriticGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Scraper & Recommender")
        self.root.geometry("800x600")
        
        # Initialize variables
        self.scraper_running = False
        self.recommender = None
        self.current_data = None
        
        # Set up logging
        self.setup_logging()
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.scraper_tab = ttk.Frame(self.notebook)
        self.recommender_tab = ttk.Frame(self.notebook)
        self.visualization_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.scraper_tab, text='Scraper')
        self.notebook.add(self.recommender_tab, text='Recommender')
        self.notebook.add(self.visualization_tab, text='Visualization')
        
        # Set up each tab
        self.setup_scraper_tab()
        self.setup_recommender_tab()
        self.setup_visualization_tab()
        
        # Status bar at the bottom
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.set_status("Ready")
        
    def setup_logging(self):
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = os.path.join(log_dir, f'metacritic_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def setup_scraper_tab(self):
        """Set up the scraper tab interface"""
        # URL Input Frame
        url_frame = ttk.LabelFrame(self.scraper_tab, text="URL Input", padding=10)
        url_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # URL entry
        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Add URL button
        add_url_btn = ttk.Button(url_frame, text="Add URL", command=self.add_url)
        add_url_btn.pack(side=tk.LEFT)
        
        # URL List Frame
        url_list_frame = ttk.LabelFrame(self.scraper_tab, text="URLs to Scrape", padding=10)
        url_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # URL Listbox with scrollbar
        self.url_listbox = tk.Listbox(url_list_frame)
        scrollbar = ttk.Scrollbar(url_list_frame, orient=tk.VERTICAL, command=self.url_listbox.yview)
        self.url_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.url_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control Buttons Frame
        control_frame = ttk.Frame(self.scraper_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Buttons
        ttk.Button(control_frame, text="Remove Selected", command=self.remove_url).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear All", command=self.clear_urls).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Load URLs from File", command=self.load_urls).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Start Scraping", command=self.start_scraping).pack(side=tk.LEFT, padx=5)
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(self.scraper_tab, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X)
        
    def setup_recommender_tab(self):
        """Set up the recommender tab interface"""
        # Search Frame
        search_frame = ttk.LabelFrame(self.recommender_tab, text="Find Game", padding=10)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Game search entry
        self.game_search_entry = ttk.Entry(search_frame)
        self.game_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Search button
        search_btn = ttk.Button(search_frame, text="Get Recommendations", command=self.get_recommendations)
        search_btn.pack(side=tk.LEFT)
        
        # Recommendations Display
        rec_frame = ttk.LabelFrame(self.recommender_tab, text="Recommendations", padding=10)
        rec_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create text widget for recommendations
        self.rec_text = scrolledtext.ScrolledText(rec_frame, wrap=tk.WORD)
        self.rec_text.pack(fill=tk.BOTH, expand=True)
        
        # Preferences Frame
        pref_frame = ttk.LabelFrame(self.recommender_tab, text="Preferences", padding=10)
        pref_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add preference controls (sliders for different aspects)
        self.setup_preference_controls(pref_frame)
        
    def setup_visualization_tab(self):
    # Controls Frame
        controls_frame = ttk.Frame(self.visualization_tab)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Refresh Data", command=self.refresh_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Export Data", command=self.export_data).pack(side=tk.LEFT, padx=5)
        
        # Create Treeview with scrollbars
        tree_frame = ttk.Frame(self.visualization_tab)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(tree_frame)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        
    def setup_preference_controls(self, parent):
        """Set up preference sliders"""
        # Create preference sliders
        preferences = ['Action', 'Adventure', 'RPG', 'Strategy', 'Simulation', 'Puzzle', 'Horror']
        self.preference_vars = {}
        
        for pref in preferences:
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(frame, text=pref).pack(side=tk.LEFT)
            var = tk.DoubleVar(value=0.5)
            self.preference_vars[pref] = var
            
            slider = ttk.Scale(frame, from_=0, to=1, variable=var, orient=tk.HORIZONTAL)
            slider.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            
    def add_url(self):
        """Add URL to the listbox"""
        url = self.url_entry.get().strip()
        if url:
            if url.startswith('https://www.metacritic.com/game/'):
                self.url_listbox.insert(tk.END, url)
                self.url_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Invalid URL", "Please enter a valid Metacritic game URL.")
                
    def remove_url(self):
        """Remove selected URL from the listbox"""
        selection = self.url_listbox.curselection()
        if selection:
            self.url_listbox.delete(selection)
            
    def clear_urls(self):
        """Clear all URLs from the listbox"""
        self.url_listbox.delete(0, tk.END)
        
    def load_urls(self):
        """Load URLs from a text file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    urls = f.readlines()
                for url in urls:
                    url = url.strip()
                    if url.startswith('https://www.metacritic.com/game/'):
                        self.url_listbox.insert(tk.END, url)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading URLs: {str(e)}")
                
    def start_scraping(self):
        """Start the scraping process"""
        if not self.scraper_running:
            urls = list(self.url_listbox.get(0, tk.END))
            if not urls:
                messagebox.showwarning("No URLs", "Please add some URLs to scrape.")
                return
                
            self.scraper_running = True
            threading.Thread(target=self.scrape_urls, args=(urls,), daemon=True).start()
            
    def scrape_urls(self, urls):
        """Scrape URLs in a separate thread"""
        try:
            from metacritic import scrape_multiple_games, save_to_csv, validate_metacritic_url
            
            invalid_urls = [url for url in urls if not validate_metacritic_url(url)]
            if invalid_urls:
                self.set_status("Invalid URLs detected")
                messagebox.showwarning("Invalid URLs", 
                    f"Some URLs are invalid and will be skipped:\n{'n'.join(invalid_urls)}")
                return
            
            total = len(urls)
            processed = 0
            
            def update_progress(future):
                nonlocal processed
                processed =+ 1
                self.progress_var.set((processed/total) * 100)
                self.status(f"Processed {processed}/{total} URLs")
            
            for i, url in enumerate(urls, 1):
                self.progress_var.set((i / total) * 100)
                self.set_status(f"Scraping {i}/{total}: {url}")
                
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for url in urls:
                    future = executor.submit(scrape_metacritic, url)
                    future.add_done_callback(update_progress)
                    futures.add(future)
                    
                results = []
                for future in futures:
                    try:
                        result = future.result()
                        if result:
                            results.append(result)
                    except Exception as e:
                        logging.error(f"Error scraping URL: {str(e)}")
                        
                if results:
                    save_to_csv(results)
                    self.set_status("Scraping completed successfully!")
                    messagebox.showinfo("Success", 
                        f"Successfully scraped {len(results)} games!")
                else:
                    self.set_status("No data was scraped")
                    messagebox.showwarning("No Data", 
                        "No game data was successfully scraped")
                
        except Exception as e:
            self.set_status(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred while scraping: {str(e)}")
        
        finally:
            self.scraper_running = False
            self.progress_var.set(0)
            
    def get_recommendations(self):
        game_title = self.game_search_entry.get().strip()
        if not game_title:
            messagebox.showwarning("No Game", "Please enter a game title.")
            return
            
        try:
            # Check if data file exists
            if not os.path.exists('output.csv'):
                messagebox.showerror("No Data", 
                    "Please scrape some games first before getting recommendations.")
                return
                
            if not self.recommender:
                self.recommender = GameRecommender('output.csv')
                self.recommender.train_model()
                
            # Get preferences
            preferences = {k: v.get() for k, v in self.preference_vars.items()}
            
            # Get recommendations with error handling
            try:
                recommendations = self.recommender.get_recommendations(game_title)
                logging.debug(f"Raw recommendations: {recommendations}")
            except KeyError:
                messagebox.showwarning("Game Not Found", 
                    "The specified game was not found in the database.")
                return
                
            # Display recommendations
            self.rec_text.delete(1.0, tk.END)
            if recommendations:
                formatted_text = ""
                for rec in recommendations:
                    try:
                        formatted_text += self._format_recommendation(rec)
                    except Exception as e:
                        logging.error(f"Error formatting recommendation: {str(e)}")
                        continue
                
                if formatted_text:
                    self.rec_text.insert(tk.END, formatted_text)
                else:
                    self.rec_text.insert(tk.END, "Error formatting recommendations.")
            else:
                self.rec_text.insert(tk.END, "No recommendations found.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error getting recommendations: {str(e)}")
            
    def _format_recommendation(self, rec):
        formatted_text = f"\nTitle: {rec['title']}\n"
        
        try:
            similarity = float(rec['similarity_score'])
        
            if similarity < 1:
                similarity = similarity * 100
            similarity = min(similarity, 100)
        
            formatted_text += f"Similarity: {similarity:.1f}%\n"
        except (ValueError, TypeError):
            # Handle cases where similarity score might be invalid
            formatted_text += "Similarity: N/A\n"
        
        # Add metascore if available
        if 'metascore' in rec and rec['metascore']:
            formatted_text += f"Metascore: {rec['metascore']}\n"
            
        # Add genres if available, formatting them nicely
        if 'genres' in rec and rec['genres']:
            # Handle both string and list formats for genres
            if isinstance(rec['genres'], str):
                genres = rec['genres'].split(',')
            else:
                genres = rec['genres']
            formatted_text += f"Genres: {', '.join(genres)}\n"
            
        formatted_text += "-" * 50 + "\n"
    
        return formatted_text
            
    def refresh_data(self):
        """Refresh the data viewer"""
        try:
            self.current_data = pd.read_csv('output.csv')
            self.update_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading data: {str(e)}")
            
    def update_treeview(self):
        """Update the treeview with current data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if self.current_data is not None:
            # Configure columns
            self.tree["columns"] = list(self.current_data.columns)
            for col in self.current_data.columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100)
                
            # Add data
            for i, row in self.current_data.iterrows():
                self.tree.insert("", "end", values=list(row))
                
    def export_data(self):
        """Export the current data to a file"""
        if self.current_data is not None:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            if filename:
                try:
                    self.current_data.to_csv(filename, index=False)
                    messagebox.showinfo("Success", "Data exported successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Error exporting data: {str(e)}")
                    
    def set_status(self, message):
        """Update the status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
if __name__ == "__main__":
    root = tk.Tk()
    app = MetacriticGUI(root)
    root.mainloop()