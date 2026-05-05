import customtkinter as ctk
from collections import Counter
from datetime import datetime
from .pdf_generator import PDFGenerator

try:
    import matplotlib

    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.ticker import MaxNLocator  # 🚀 POGI UPDATE: Para whole numbers lang sa graphs!

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class OverviewPage:
    def __init__(self, parent_frame, engine, user_data):
        self.engine = engine
        self.user = user_data

        self.bg_color = "#F8F9F5"
        self.text_dark = "#2B2B2B"

        # Chart Colors
        self.chart_cyan = "#00BCD4"
        self.chart_blue = "#4285F4"
        self.chart_dark_blue = "#3F51B5"

        self.container = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.all_incidents = self.engine.get_all_incidents()

        self.canvases = {}

        self.build_ui()

    def build_ui(self):
        # 1. HEADER WITH PDF EXPORT
        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 10))
        ctk.CTkLabel(header_frame, text="📊 Analytics Dashboard", font=("Arial", 28, "bold"), text_color="#1D2153").pack(
            side="left")

        export_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        export_frame.pack(side="right")

        self.report_timeframe = ctk.StringVar(value="This Month")
        ctk.CTkOptionMenu(export_frame, variable=self.report_timeframe,
                          values=["This Week", "This Month", "This Year", "All Time"], fg_color="#1D2153").pack(
            side="left", padx=10)

        ctk.CTkButton(export_frame, text="🖨️ Export PDF", fg_color="#27AE60", hover_color="#1E8449",
                      command=lambda: PDFGenerator.export_analytics(
                          self.engine.get_timeframe_analytics(self.report_timeframe.get()),
                          self.report_timeframe.get())).pack(side="left")

        # 2. THE STAT CARDS
        self.build_stat_cards(self.container)

        if not MATPLOTLIB_AVAILABLE:
            error_frame = ctk.CTkFrame(self.container, fg_color="#FADBD8", corner_radius=10)
            error_frame.pack(fill="x", padx=30, pady=20)
            ctk.CTkLabel(error_frame,
                         text="⚠️ Matplotlib is missing! Please run 'pip install matplotlib' in your terminal.",
                         text_color="#C0392B", font=("Arial", 14, "bold")).pack(pady=20)
            return

        # 3. TOP ROW CHARTS
        top_row = ctk.CTkFrame(self.container, fg_color="transparent")
        top_row.pack(fill="x", padx=25, pady=10)
        top_row.grid_columnconfigure((0, 1), weight=1)

        self.setup_donut_section(top_row)
        self.setup_monthly_section(top_row)

        # 4. BOTTOM ROW CHARTS
        bottom_row = ctk.CTkFrame(self.container, fg_color="transparent")
        bottom_row.pack(fill="x", padx=25, pady=20)

        self.setup_peak_hours_section(bottom_row)

    # ==========================================
    # STAT CARDS UI LOGIC
    # ==========================================
    def build_stat_cards(self, parent):
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.pack(fill="x", padx=25, pady=(0, 15))

        stats = self.engine.get_dashboard_stats()

        # 🚀 POGI UPDATE: Updated Labels ("Normal" at "High Priority")
        self.create_stat_card(stats_frame, "Total Cases", str(stats.get('Total Cases', 0)), "📋", "#E74C3C")
        self.create_stat_card(stats_frame, "Resolved", str(stats.get('Resolved', 0)), "✅", "#27AE60")
        self.create_stat_card(stats_frame, "Normal", str(stats.get('Pending', 0)), "⏳", "#F39C12")
        self.create_stat_card(stats_frame, "High Priority", str(stats.get('Urgent', 0)), "🚨", "#1D2153")

    def create_stat_card(self, parent, title, value, icon, color):
        card = ctk.CTkFrame(parent, fg_color="white", border_color=color, border_width=1, corner_radius=8, height=80)
        card.pack(side="left", fill="x", expand=True, padx=5)
        card.pack_propagate(False)

        icon_lbl = ctk.CTkLabel(card, text=icon, font=("Arial", 36))
        icon_lbl.place(relx=0.15, rely=0.5, anchor="center")

        text_frame = ctk.CTkFrame(card, fg_color="transparent")
        text_frame.place(relx=0.85, rely=0.5, anchor="e")

        ctk.CTkLabel(text_frame, text=title, font=("Arial", 12, "bold"), text_color=color).pack(anchor="e")
        ctk.CTkLabel(text_frame, text=value, font=("Arial", 28, "bold"), text_color=color).pack(anchor="e", pady=(2, 0))

    # ==========================================
    # LOGIC: REFRESHING THE CHARTS (REAL-TIME)
    # ==========================================
    def update_donut(self, choice):
        filtered = self.all_incidents if choice == "All Category" else [r for r in self.all_incidents if
                                                                        r.get('category') == choice]
        self.draw_donut(filtered)

    def update_monthly(self, choice):
        current_year = datetime.now().year
        if choice == "This Year":
            filtered = [r for r in self.all_incidents if
                        str(r.get('date_of_incident') or "").startswith(str(current_year))]
        else:
            filtered = self.all_incidents
        self.draw_monthly(filtered)

    def update_peak(self, choice):
        if choice == "AM":
            filtered = [r for r in self.all_incidents if "AM" in str(r.get('exact_time'))]
        elif choice == "PM":
            filtered = [r for r in self.all_incidents if "PM" in str(r.get('exact_time'))]
        else:
            filtered = self.all_incidents
        self.draw_peak(filtered)

    # ==========================================
    # DONUT CHART SETUP & DRAW
    # ==========================================
    def setup_donut_section(self, parent):
        self.donut_card = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, border_width=1,
                                       border_color="#E0E0E0")
        self.donut_card.grid(row=0, column=0, padx=10, sticky="nsew")

        top = ctk.CTkFrame(self.donut_card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(top, text="🕒 Complaint Distribution", font=("Arial", 16, "bold"), text_color=self.text_dark).pack(
            anchor="w")

        cats = ["All Category"] + self.engine.get_incident_categories()
        ctk.CTkComboBox(top, values=cats, command=self.update_donut, width=150, fg_color="white",
                        text_color="black").pack(anchor="w", pady=(10, 0))

        self.donut_plot_cont = ctk.CTkFrame(self.donut_card, fg_color="transparent")
        self.donut_plot_cont.pack(fill="both", expand=True)
        self.draw_donut(self.all_incidents)

    def draw_donut(self, data):
        for w in self.donut_plot_cont.winfo_children(): w.destroy()

        counts = Counter([r.get('category', 'Uncategorized') for r in data if r.get('category')])
        if not counts: return ctk.CTkLabel(self.donut_plot_cont, text="No Data Available", text_color="gray").pack(
            pady=50)

        labels = list(counts.keys())[:3]
        sizes = [counts[k] for k in labels]
        colors = [self.chart_cyan, self.chart_blue, self.chart_dark_blue]

        fig = Figure(figsize=(4, 3.5), dpi=100)
        fig.patch.set_facecolor('white')
        ax = fig.add_subplot(111)

        wedges, _ = ax.pie(sizes, colors=colors, startangle=90, wedgeprops=dict(width=0.5, edgecolor='w'))
        ax.axis('equal')
        ax.legend(wedges, labels, loc="lower center", bbox_to_anchor=(0.5, -0.1), ncol=3, frameon=False)

        canvas = FigureCanvasTkAgg(fig, master=self.donut_plot_cont)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ==========================================
    # MONTHLY TREND CHART SETUP & DRAW
    # ==========================================
    def setup_monthly_section(self, parent):
        self.monthly_card = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, border_width=1,
                                         border_color="#E0E0E0")
        self.monthly_card.grid(row=0, column=1, padx=10, sticky="nsew")

        top = ctk.CTkFrame(self.monthly_card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(top, text="📈 Monthly Complaint Trend", font=("Arial", 16, "bold"), text_color=self.text_dark).pack(
            anchor="w")

        ctk.CTkComboBox(top, values=["All Months", "This Year"], command=self.update_monthly, width=150,
                        fg_color="white", text_color="black").pack(anchor="w", pady=(10, 0))

        self.monthly_plot_cont = ctk.CTkFrame(self.monthly_card, fg_color="transparent")
        self.monthly_plot_cont.pack(fill="both", expand=True)
        self.draw_monthly(self.all_incidents)

    def draw_monthly(self, data):
        for w in self.monthly_plot_cont.winfo_children(): w.destroy()

        months = []
        for r in data:
            d = r.get('date_of_incident') or r.get('created_at')
            if d: months.append(d.strftime("%b") if not isinstance(d, str) else d)

        counts = Counter(months)
        if not counts: return ctk.CTkLabel(self.monthly_plot_cont, text="No Data Available", text_color="gray").pack(
            pady=50)

        fig = Figure(figsize=(4, 3.5), dpi=100)
        fig.patch.set_facecolor('white')
        ax = fig.add_subplot(111)

        ax.bar(list(counts.keys())[:4], list(counts.values())[:4], color=self.chart_cyan, width=0.7)
        ax.spines[['top', 'right', 'left']].set_visible(False)
        ax.yaxis.grid(True, color='#E0E0E0', linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        ax.tick_params(axis='both', which='both', length=0, labelsize=9, colors='gray')

        # 🚀 POGI UPDATE: Whole Numbers Only!
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        canvas = FigureCanvasTkAgg(fig, master=self.monthly_plot_cont)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # ==========================================
    # PEAK HOURS CHART SETUP & DRAW
    # ==========================================
    def setup_peak_hours_section(self, parent):
        self.peak_card = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, border_width=1,
                                      border_color="#E0E0E0")
        self.peak_card.pack(fill="x", padx=10)

        top = ctk.CTkFrame(self.peak_card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(top, text="🕒 Peak Complaint Hours", font=("Arial", 16, "bold"), text_color=self.text_dark).pack(
            anchor="w")

        ctk.CTkComboBox(top, values=["Time", "AM", "PM"], command=self.update_peak, width=150, fg_color="white",
                        text_color="black").pack(anchor="w", pady=(10, 0))

        self.peak_plot_cont = ctk.CTkFrame(self.peak_card, fg_color="transparent")
        self.peak_plot_cont.pack(fill="both", expand=True)
        self.draw_peak(self.all_incidents)

    def draw_peak(self, data):
        for w in self.peak_plot_cont.winfo_children(): w.destroy()

        hours = []
        for r in data:
            t_str = r.get('exact_time')
            if t_str:
                try:
                    hours.append(datetime.strptime(t_str, "%I:%M %p").strftime("%I %p").lstrip("0"))
                except:
                    pass

        counts = Counter(hours)
        if not counts: return ctk.CTkLabel(self.peak_plot_cont, text="No Data Available", text_color="gray").pack(
            pady=30)

        top_hours = counts.most_common(4)
        labels = [h[0] for h in top_hours]
        values = [h[1] for h in top_hours]

        fig = Figure(figsize=(10, 3.5), dpi=100)
        fig.patch.set_facecolor('white')
        ax = fig.add_subplot(111)

        ax.barh(labels, values, color=self.chart_blue, height=0.7)
        ax.invert_yaxis()
        ax.spines[['top', 'right', 'bottom', 'left']].set_visible(False)
        ax.xaxis.grid(True, color='#E0E0E0', linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        ax.tick_params(axis='both', which='both', length=0, labelsize=9, colors='gray')

        # 🚀 POGI UPDATE: Whole Numbers Only!
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        canvas = FigureCanvasTkAgg(fig, master=self.peak_plot_cont)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 20))
