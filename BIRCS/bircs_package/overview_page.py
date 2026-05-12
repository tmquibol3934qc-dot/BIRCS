import customtkinter as ctk
from collections import Counter
from datetime import datetime
from .pdf_generator import PDFGenerator

try:
    import matplotlib

    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.ticker import MaxNLocator

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class OverviewPage:
    def __init__(self, parent_frame, engine, user_data):
        self.engine = engine
        self.user = user_data

        # 🎨 THE PREMIUM WEB PALETTE
        self.color_sidebar = "#1D2153"  # Deep Navy
        self.color_bg = "#F4F6F7"       # Web Canvas Gray
        self.color_card = "#FFFFFF"     # Crisp White
        self.color_border = "#EAECEE"   # Subtle borders
        self.primary = "#27AE60"        # Emerald Green (Resolved)
        self.orange = "#E05D3A"         # Alert Orange (Pending)
        self.red = "#E74C3C"            # Danger Red (Urgent)
        self.chart_blue = "#3498DB"     # Clean Blue for generic stats
        self.text_dark = "#2C3E50"
        self.text_muted = "#7F8C8D"

        # 🚀 SINGLE SOSYALIN FONT STANDARD
        self.ui_font = "Poppins"

        self.container = ctk.CTkScrollableFrame(parent_frame, fg_color=self.color_bg)
        self.container.pack(fill="both", expand=True)

        try:
            self.all_incidents = self.engine.advanced_search_incidents("", "All Categories")
            if not self.all_incidents:
                self.all_incidents = self.engine.get_all_incidents()
        except Exception:
            self.all_incidents = self.engine.get_all_incidents()

        self.canvases = {}
        self.build_ui()

    def build_ui(self):
        # 📌 1. HEADER WITH PDF EXPORT
        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", padx=35, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="📊 Analytics Dashboard", font=(self.ui_font, 28, "bold"),
                     text_color=self.color_sidebar).pack(side="left")

        export_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        # 🚀 THE POGI FIX: Umatras tayo ng 80 pixels pakaliwa para hindi mabangga ang Profile Button!
        export_frame.pack(side="right", padx=(0, 80))

        self.report_timeframe = ctk.StringVar(value="This Month")
        dropdown = ctk.CTkOptionMenu(export_frame, variable=self.report_timeframe,
                                     values=["This Week", "This Month", "This Year", "All Time"],
                                     fg_color="#FDFCF6", text_color=self.text_dark, button_color=self.color_border,
                                     button_hover_color="#D5D8DC", font=(self.ui_font, 12, "bold"))
        dropdown.pack(side="left", padx=15)

        ctk.CTkButton(export_frame, text="🖨️ Export PDF Report", fg_color=self.primary, hover_color="#1E8449",
                      font=(self.ui_font, 12, "bold"), height=35, corner_radius=8,
                      command=lambda: PDFGenerator.export_analytics(
                          self.engine.get_timeframe_analytics(self.report_timeframe.get()),
                          self.report_timeframe.get())).pack(side="left")

        # 📌 2. THE STAT CARDS (Bento Box Style)
        self.build_stat_cards(self.container)

        if not MATPLOTLIB_AVAILABLE:
            error_frame = ctk.CTkFrame(self.container, fg_color="#FDEDEC", corner_radius=10, border_width=1,
                                       border_color="#F5B7B1")
            error_frame.pack(fill="x", padx=35, pady=20)
            ctk.CTkLabel(error_frame,
                         text="⚠️ Matplotlib is missing! Please run 'pip install matplotlib' in your terminal.",
                         text_color="#C0392B", font=(self.ui_font, 14, "bold")).pack(pady=20)
            return

        # 📌 3. TOP ROW CHARTS (Donut & Monthly Line Graph)
        top_row = ctk.CTkFrame(self.container, fg_color="transparent")
        top_row.pack(fill="x", padx=25, pady=10)
        top_row.grid_columnconfigure(0, weight=1)
        top_row.grid_columnconfigure(1, weight=2)  # Line graph gets more space to breathe

        self.setup_donut_section(top_row)
        self.setup_monthly_section(top_row)

        # 📌 4. BOTTOM ROW CHARTS (Peak Hours Bar)
        bottom_row = ctk.CTkFrame(self.container, fg_color="transparent")
        bottom_row.pack(fill="x", padx=25, pady=(10, 30))

        self.setup_peak_hours_section(bottom_row)

    # ==========================================
    # STAT CARDS UI LOGIC
    # ==========================================
    def build_stat_cards(self, parent):
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=(0, 20))

        total_cases = len(self.all_incidents)
        resolved_count = sum(1 for r in self.all_incidents if r.get('status') in ['Resolved', 'Completed'])
        pending_count = sum(1 for r in self.all_incidents if r.get('status') == 'Pending')
        urgent_count = sum(1 for r in self.all_incidents if r.get('status') == 'Urgent')

        self.create_stat_card(stats_frame, "Total Records", str(total_cases), "📁", self.color_sidebar)
        self.create_stat_card(stats_frame, "Resolved", str(resolved_count), "✅", self.primary)
        self.create_stat_card(stats_frame, "Routine / Pending", str(pending_count), "⏳", self.orange)
        self.create_stat_card(stats_frame, "High Priority", str(urgent_count), "🚨", self.red)

    def create_stat_card(self, parent, title, value, icon, color):
        card = ctk.CTkFrame(parent, fg_color=self.color_card, border_color=self.color_border, border_width=1,
                            corner_radius=12, height=100)
        card.pack(side="left", fill="x", expand=True, padx=8)
        card.pack_propagate(False)

        # Icon Frame
        icon_lbl = ctk.CTkLabel(card, text=icon, font=(self.ui_font, 36))
        icon_lbl.place(relx=0.15, rely=0.5, anchor="center")

        # Text Frame
        text_frame = ctk.CTkFrame(card, fg_color="transparent")
        text_frame.place(relx=0.85, rely=0.5, anchor="e")

        ctk.CTkLabel(text_frame, text=title, font=(self.ui_font, 12, "bold"), text_color=self.text_muted).pack(
            anchor="e")
        ctk.CTkLabel(text_frame, text=value, font=(self.ui_font, 30, "bold"), text_color=color).pack(anchor="e",
                                                                                                         pady=(0, 0))

    # ==========================================
    # LOGIC: REFRESHING THE CHARTS (REAL-TIME)
    # ==========================================
    def update_donut(self, choice):
        filtered = self.all_incidents if choice == "All Categories" else [r for r in self.all_incidents if
                                                                          r.get('category') == choice]
        self.draw_donut(filtered)

    def update_monthly(self, selected_year):
        filtered = []
        for r in self.all_incidents:
            date_val = r.get('date_of_incident') or r.get('created_at')
            if date_val:
                if isinstance(date_val, str) and str(selected_year) in date_val:
                    filtered.append(r)
                elif not isinstance(date_val, str) and str(date_val.year) == str(selected_year):
                    filtered.append(r)
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
        self.donut_card = ctk.CTkFrame(parent, fg_color=self.color_card, corner_radius=12, border_width=1,
                                       border_color=self.color_border)
        self.donut_card.grid(row=0, column=0, padx=8, sticky="nsew")

        top = ctk.CTkFrame(self.donut_card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(top, text="Distribution", font=(self.ui_font, 16, "bold"), text_color=self.color_sidebar).pack(
            anchor="w")

        cats = ["All Categories"] + self.engine.get_incident_categories()
        ctk.CTkOptionMenu(top, values=cats, command=self.update_donut, width=150, fg_color="#F8F9FA",
                          text_color=self.text_dark,
                          button_color=self.color_border, button_hover_color="#D5D8DC", font=(self.ui_font, 11)).pack(
            anchor="w", pady=(5, 0))

        self.donut_plot_cont = ctk.CTkFrame(self.donut_card, fg_color="transparent")
        self.donut_plot_cont.pack(fill="both", expand=True)
        self.draw_donut(self.all_incidents)

    def draw_donut(self, data):
        for w in self.donut_plot_cont.winfo_children(): w.destroy()

        counts = Counter([str(r.get('category')).strip() if r.get('category') and str(
            r.get('category')).strip() != "" else 'Uncategorized' for r in data])

        if not sum(counts.values()):
            return ctk.CTkLabel(self.donut_plot_cont, text="No Data Available", text_color=self.text_muted,
                                font=(self.ui_font, 12, "italic")).pack(pady=50)

        labels = list(counts.keys())
        sizes = list(counts.values())
        total_cases = sum(sizes)

        labels_with_counts = [f"{lbl} ({sz} - {(sz / total_cases) * 100:.1f}%)" for lbl, sz in zip(labels, sizes)]

        color_palette = [self.chart_blue, self.primary, self.orange, self.color_sidebar, self.red, "#9B59B6", "#16A085"]
        colors = [color_palette[i % len(color_palette)] for i in range(len(labels))]

        fig = Figure(figsize=(4, 4.5), dpi=100)
        fig.patch.set_facecolor('#FFFFFF')

        ax = fig.add_axes([0.1, 0.35, 0.8, 0.6])
        wedges, _ = ax.pie(sizes, colors=colors, startangle=90, wedgeprops=dict(width=0.4, edgecolor='w', linewidth=2))
        ax.axis('equal')

        fig.legend(wedges, labels_with_counts, loc="lower center", ncol=1, frameon=False, fontsize=9)

        canvas = FigureCanvasTkAgg(fig, master=self.donut_plot_cont)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ==========================================
    # 📈 MONTHLY AREA-LINE CHART
    # ==========================================
    def setup_monthly_section(self, parent):
        self.monthly_card = ctk.CTkFrame(parent, fg_color=self.color_card, corner_radius=12, border_width=1,
                                         border_color=self.color_border)
        self.monthly_card.grid(row=0, column=1, padx=8, sticky="nsew")

        top = ctk.CTkFrame(self.monthly_card, fg_color="transparent")
        top.pack(fill="x", padx=25, pady=20)
        ctk.CTkLabel(top, text="📈 Monthly Incident Trends", font=(self.ui_font, 16, "bold"),
                     text_color=self.color_sidebar).pack(anchor="w")

        available_years = set()
        for r in self.all_incidents:
            date_val = r.get('date_of_incident') or r.get('created_at')
            if date_val:
                if isinstance(date_val, str):
                    if '/' in date_val:
                        available_years.add(date_val.split('/')[-1])
                    elif '-' in date_val:
                        available_years.add(date_val.split('-')[0])
                else:
                    available_years.add(str(date_val.year))

        years_list = sorted(list(available_years), reverse=True)
        if not years_list: years_list = [str(datetime.now().year)]

        self.year_var = ctk.StringVar(value=years_list[0])
        ctk.CTkOptionMenu(top, variable=self.year_var, values=years_list, command=self.update_monthly, width=120,
                          fg_color="#F8F9FA", text_color=self.text_dark, button_color=self.color_border,
                          button_hover_color="#D5D8DC", font=(self.ui_font, 11, "bold")).pack(anchor="w", pady=(5, 0))

        self.monthly_plot_cont = ctk.CTkFrame(self.monthly_card, fg_color="transparent")
        self.monthly_plot_cont.pack(fill="both", expand=True)

        self.update_monthly(self.year_var.get())

    def draw_monthly(self, data):
        for w in self.monthly_plot_cont.winfo_children(): w.destroy()

        months_data = []
        for r in data:
            d = r.get('date_of_incident') or r.get('created_at')
            if d:
                if isinstance(d, str):
                    try:
                        if '/' in d:
                            m_num = int(d.split('/')[0])
                            months_data.append(datetime(2000, m_num, 1).strftime("%b"))
                        elif '-' in d:
                            months_data.append(datetime.strptime(d.split()[0], "%Y-%m-%d").strftime("%b"))
                    except:
                        pass
                else:
                    months_data.append(d.strftime("%b"))

        counts = Counter(months_data)
        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        values = [counts.get(m, 0) for m in month_order]

        fig = Figure(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor('#FFFFFF')
        ax = fig.add_subplot(111)

        ax.plot(month_order, values, color=self.chart_blue, marker='o', linewidth=3, markersize=6,
                markerfacecolor="white", markeredgewidth=2)
        ax.fill_between(month_order, values, color=self.chart_blue, alpha=0.1)

        ax.spines[['top', 'right']].set_visible(False)
        ax.spines['left'].set_color('#E0E0E0')
        ax.spines['bottom'].set_color('#E0E0E0')

        ax.yaxis.grid(True, color='#F0F0F0', linestyle='--', linewidth=1)
        ax.set_axisbelow(True)

        ax.tick_params(axis='x', colors=self.text_muted, labelsize=9)
        ax.tick_params(axis='y', length=0, labelsize=9, colors=self.text_muted)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        max_val = max(values) if values else 1
        ax.set_ylim(0, max_val + (max_val * 0.1) + 1)

        canvas = FigureCanvasTkAgg(fig, master=self.monthly_plot_cont)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # ==========================================
    # PEAK HOURS CHART SETUP & DRAW
    # ==========================================
    def setup_peak_hours_section(self, parent):
        self.peak_card = ctk.CTkFrame(parent, fg_color=self.color_card, corner_radius=12, border_width=1,
                                      border_color=self.color_border)
        self.peak_card.pack(fill="x", padx=8)

        top = ctk.CTkFrame(self.peak_card, fg_color="transparent")
        top.pack(fill="x", padx=25, pady=20)
        ctk.CTkLabel(top, text="🕒 Peak Incident Hours", font=(self.ui_font, 16, "bold"),
                     text_color=self.color_sidebar).pack(anchor="w")

        ctk.CTkOptionMenu(top, values=["Time", "AM", "PM"], command=self.update_peak, width=120, fg_color="#F8F9FA",
                          text_color=self.text_dark, button_color=self.color_border, button_hover_color="#D5D8DC",
                          font=(self.ui_font, 11)).pack(anchor="w", pady=(5, 0))

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
        if not counts:
            return ctk.CTkLabel(self.peak_plot_cont, text="No Data Available", text_color=self.text_muted,
                                font=(self.ui_font, 12, "italic")).pack(pady=30)

        top_hours = counts.most_common(5)
        labels = [h[0] for h in top_hours]
        values = [h[1] for h in top_hours]

        fig = Figure(figsize=(10, 3.5), dpi=100)
        fig.patch.set_facecolor('#FFFFFF')
        ax = fig.add_subplot(111)

        ax.barh(labels, values, color=self.primary, height=0.5, edgecolor="white")
        ax.invert_yaxis()

        ax.spines[['top', 'right', 'bottom']].set_visible(False)
        ax.spines['left'].set_color('#E0E0E0')
        ax.xaxis.grid(True, color='#F0F0F0', linestyle='--', linewidth=1)
        ax.set_axisbelow(True)

        ax.tick_params(axis='both', which='both', length=0, labelsize=10, colors=self.text_muted)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        canvas = FigureCanvasTkAgg(fig, master=self.peak_plot_cont)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 20))
