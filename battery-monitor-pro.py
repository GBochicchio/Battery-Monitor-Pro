import psutil
import tkinter as tk
import threading
import time
from datetime import datetime
import argparse
import logging
import sys
import math

# ========== CONFIGURAZIONI ==========
DEFAULT_MIN_THRESHOLD = 20          # Soglia minima percentuale
DEFAULT_MAX_THRESHOLD = 80          # Soglia massima percentuale
DEFAULT_CHECK_INTERVAL = 300        # Intervallo controllo in secondi (5 minuti)
PROGRESSIVE_REMINDER_STEP = 5       # Promemoria ogni 5% sopra la soglia massima

# Configurazioni popup
TIMEOUT_BATTERIA_CARICA = 30       # Auto-chiudi dopo 30 secondi
TIMEOUT_BATTERIA_SCARICA = 90      # Auto-chiudi dopo 90 secondi  
TIMEOUT_BATTERIA_CRITICA = 0       # Mai auto-chiudi se <15%
AUTO_CLOSE_ON_POWER_CHANGE = True  # Chiudi se cambia alimentazione
POWER_CHECK_INTERVAL = 2           # Controlla alimentazione ogni 2 secondi

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("battery_monitor.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ModernBatteryPopup:
    def __init__(self):
        self.root = None
        self.popup_attiva = False
        self.animazione_attiva = False
        self.power_monitor_active = False
        self.initial_power_state = None
        self.tipo_popup = None
        self.chiusura_forzata = False
        self.countdown_attivo = False
        self.countdown_job = None
        self.power_monitor_job = None
        self.animation_job = None
    
    def mostra_popup_batteria_scarica(self, percentuale, tempo_rimasto="N/A"):
        """Mostra popup moderno per batteria scarica"""
        if self.popup_attiva:
            return
        
        self.popup_attiva = True
        self.tipo_popup = "scarica"
        self.initial_power_state = self.get_power_state()
        
        self.crea_finestra_moderna(
            titolo="Batteria Scarica",
            percentuale=percentuale,
            tempo_rimasto=tempo_rimasto,
            tipo="scarica"
        )
    
    def mostra_popup_batteria_carica(self, percentuale, soglia_max=80):
        """Mostra popup moderno per batteria carica"""
        if self.popup_attiva:
            return
        
        self.popup_attiva = True
        self.tipo_popup = "carica"
        self.initial_power_state = self.get_power_state()
        
        # Calcola quanti step sopra la soglia siamo
        steps_over = max(0, (percentuale - soglia_max) // PROGRESSIVE_REMINDER_STEP)
        
        self.crea_finestra_moderna(
            titolo="Batteria Carica",
            percentuale=percentuale,
            tempo_rimasto=None,
            tipo="carica",
            steps_over=steps_over,
            soglia_max=soglia_max
        )
    
    def get_power_state(self):
        """Ottiene lo stato attuale dell'alimentazione"""
        try:
            battery = psutil.sensors_battery()
            return battery.power_plugged if battery else None
        except:
            return None
    
    def cancel_scheduled_jobs(self):
        """Cancella tutti i job schedulati per evitare errori"""
        if self.root:
            try:
                if self.countdown_job:
                    self.root.after_cancel(self.countdown_job)
                    self.countdown_job = None
                if self.power_monitor_job:
                    self.root.after_cancel(self.power_monitor_job)
                    self.power_monitor_job = None
                if self.animation_job:
                    self.root.after_cancel(self.animation_job)
                    self.animation_job = None
            except Exception as e:
                logger.debug(f"Errore nella cancellazione dei job: {e}")
    
    def monitor_power_change(self):
        """Monitora i cambiamenti nell'alimentazione"""
        try:
            if not AUTO_CLOSE_ON_POWER_CHANGE or not self.power_monitor_active or not self.popup_attiva:
                return
            
            if not self.root or not self.root.winfo_exists():
                self.power_monitor_active = False
                return
            
            current_power_state = self.get_power_state()
            
            if current_power_state is not None and self.initial_power_state is not None:
                power_changed = current_power_state != self.initial_power_state
                
                if power_changed:
                    should_close = False
                    
                    if self.tipo_popup == "scarica" and current_power_state:
                        should_close = True
                        reason = "🔌 Alimentazione collegata"
                    elif self.tipo_popup == "carica" and not current_power_state:
                        should_close = True
                        reason = "🔋 Alimentazione scollegata"
                    
                    if should_close:
                        self.auto_close_with_reason(reason)
                        return
            
            if self.popup_attiva and self.power_monitor_active and self.root and self.root.winfo_exists():
                self.power_monitor_job = self.root.after(POWER_CHECK_INTERVAL * 1000, self.monitor_power_change)
                
        except Exception as e:
            self.power_monitor_active = False
            logger.error(f"Monitoraggio alimentazione fermato: {e}")
    
    def auto_close_with_reason(self, reason):
        """Chiude automaticamente il popup con una ragione specifica"""
        if self.popup_attiva:
            logger.info(f"Popup chiuso automaticamente: {reason}")
            self.chiudi_popup()
    
    def crea_finestra_moderna(self, titolo, percentuale, tempo_rimasto, tipo, steps_over=0, soglia_max=80):
        """Crea finestra popup moderna con design migliorato"""
        try:
            self.root = tk.Tk()
            self.root.title(titolo)
            
            # Configurazione finestra
            self.root.geometry("450x650")
            self.root.resizable(False, False)
            self.root.configure(bg='#1a1a1a')
            self.root.overrideredirect(True)
            
            # Porta in primo piano
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.focus_force()
            
            self.centra_finestra()
            self.crea_contenuto_moderno(percentuale, tempo_rimasto, tipo, steps_over, soglia_max)
            self.animazione_entrata()
            
            # Avvia monitoraggio alimentazione
            if AUTO_CLOSE_ON_POWER_CHANGE:
                self.power_monitor_active = True
                self.power_monitor_job = self.root.after(1000, self.monitor_power_change)
            
            self.configura_timeout(percentuale, tipo)
            
            # Effetti speciali per situazioni critiche
            if (tipo == "scarica" and percentuale <= 15) or (tipo == "carica" and steps_over >= 2):
                self.avvia_effetto_critico()
            
            # Gestione tasti
            self.root.bind('<Escape>', lambda e: self.chiudi_popup())
            self.root.bind('<Return>', lambda e: self.chiudi_popup())
            self.root.bind('<space>', lambda e: self.forza_chiusura())
            
            # Gestione chiusura finestra
            self.root.protocol("WM_DELETE_WINDOW", self.chiudi_popup)
            
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Errore nella creazione del popup: {e}")
            self.popup_attiva = False
    
    def configura_timeout(self, percentuale, tipo):
        """Configura il timeout automatico basato sul tipo e percentuale"""
        timeout = 0
        
        if tipo == "carica":
            timeout = TIMEOUT_BATTERIA_CARICA
        elif tipo == "scarica":
            if percentuale <= 15:
                timeout = TIMEOUT_BATTERIA_CRITICA
            else:
                timeout = TIMEOUT_BATTERIA_SCARICA
        
        if timeout > 0:
            self.avvia_countdown(timeout)
    
    def avvia_countdown(self, secondi):
        """Avvia il countdown per la chiusura automatica"""
        if not self.popup_attiva or self.chiusura_forzata:
            return
        
        self.countdown_attivo = True
        self.countdown_secondi = secondi
        self.aggiorna_countdown()
    
    def aggiorna_countdown(self):
        """Aggiorna il display del countdown"""
        try:
            if not self.popup_attiva or self.chiusura_forzata or not self.countdown_attivo:
                return
            
            if not self.root or not self.root.winfo_exists():
                self.countdown_attivo = False
                return
            
            if not hasattr(self, 'countdown_label') or not self.countdown_label.winfo_exists():
                self.countdown_attivo = False
                return
            
            if self.countdown_secondi > 0:
                minuti = self.countdown_secondi // 60
                secondi = self.countdown_secondi % 60
                if minuti > 0:
                    text = f"⏰ Chiusura automatica tra {minuti}m {secondi}s"
                else:
                    text = f"⏰ Chiusura automatica tra {secondi}s"
                
                self.countdown_label.config(text=text)
                self.countdown_secondi -= 1
                
                if self.popup_attiva and self.root and self.root.winfo_exists():
                    self.countdown_job = self.root.after(1000, self.aggiorna_countdown)
            else:
                self.auto_close_with_reason("⏰ Timeout scaduto")
                
        except Exception as e:
            self.countdown_attivo = False
            logger.error(f"Countdown fermato: {e}")
    
    def crea_contenuto_moderno(self, percentuale, tempo_rimasto, tipo, steps_over=0, soglia_max=80):
        """Crea il contenuto moderno della finestra"""
        main_frame = tk.Frame(self.root, bg='#1a1a1a', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Configurazione basata sul tipo
        if tipo == "scarica":
            header_color = "#ff4757"
            icon = "🔋"
            status_text = "BATTERIA SCARICA"
            if percentuale <= 10:
                action_text = "⚠️ CRITICO! Collega IMMEDIATAMENTE il caricatore!"
                urgency_level = "CRITICO"
            elif percentuale <= 20:
                action_text = "⚡ URGENTE! Collega il caricatore al più presto!"
                urgency_level = "URGENTE"
            else:
                action_text = "Collega il caricatore per continuare a lavorare"
                urgency_level = "NORMALE"
        else:
            header_color = "#2ed573" if steps_over == 0 else "#ff6b35"  # Arancione se step multipli
            icon = "⚡"
            
            if steps_over == 0:
                status_text = "BATTERIA CARICA"
                action_text = "Scollega il caricatore per preservare la batteria"
                urgency_level = "NORMALE"
            elif steps_over == 1:
                status_text = "BATTERIA MOLTO CARICA"
                action_text = f"⚠️ Al {percentuale}%! Scollega il caricatore ORA!"
                urgency_level = "IMPORTANTE"
            else:
                status_text = "BATTERIA SOVRACCARICA"
                action_text = f"🚨 ATTENZIONE! {percentuale}% - SCOLLEGA SUBITO!"
                urgency_level = "CRITICO"
                header_color = "#ff4757"  # Rosso per sovraccarica
        
        # Barra colorata superiore
        header_frame = tk.Frame(main_frame, bg=header_color, height=8)
        header_frame.pack(fill='x', pady=(0, 15))
        
        # Icona e titolo principale
        title_frame = tk.Frame(main_frame, bg='#1a1a1a')
        title_frame.pack(fill='x', pady=(0, 10))
        
        icon_label = tk.Label(
            title_frame,
            text=icon,
            font=("Segoe UI Emoji", 32),
            bg='#1a1a1a',
            fg=header_color
        )
        icon_label.pack()
        
        status_label = tk.Label(
            title_frame,
            text=status_text,
            font=("Segoe UI", 16, "bold"),
            bg='#1a1a1a',
            fg='white'
        )
        status_label.pack(pady=(5, 0))
        
        # Indicatore di urgenza
        if urgency_level in ["IMPORTANTE", "CRITICO"]:
            urgency_frame = tk.Frame(main_frame, bg='#333333', padx=10, pady=5)
            urgency_frame.pack(fill='x', pady=(0, 10))
            
            urgency_color = "#ff6b35" if urgency_level == "IMPORTANTE" else "#ff4757"
            urgency_text = f"🚨 LIVELLO: {urgency_level}"
            
            if tipo == "carica" and steps_over > 0:
                over_threshold = percentuale - soglia_max
                urgency_text += f" (+{over_threshold}% sopra {soglia_max}%)"
            
            urgency_label = tk.Label(
                urgency_frame,
                text=urgency_text,
                font=("Segoe UI", 10, "bold"),
                bg='#333333',
                fg=urgency_color
            )
            urgency_label.pack()
        
        # Barra di percentuale
        self.crea_barra_percentuale(main_frame, percentuale, header_color, soglia_max if tipo == "carica" else None)
        
        # Informazioni dettagliate
        info_frame = tk.Frame(main_frame, bg='#2d2d2d', padx=20, pady=15)
        info_frame.pack(fill='x', pady=(15, 10))
        
        # Percentuale grande
        perc_label = tk.Label(
            info_frame,
            text=f"{percentuale}%",
            font=("Segoe UI", 28, "bold"),
            bg='#2d2d2d',
            fg=header_color
        )
        perc_label.pack()
        
        # Informazioni aggiuntive
        if tempo_rimasto and tipo == "scarica":
            tempo_label = tk.Label(
                info_frame,
                text=f"⏱️ Tempo rimasto: {tempo_rimasto}",
                font=("Segoe UI", 11),
                bg='#2d2d2d',
                fg='#cccccc'
            )
            tempo_label.pack(pady=(5, 0))
        
        # Messaggio di azione
        action_label = tk.Label(
            main_frame,
            text=action_text,
            font=("Segoe UI", 12, "bold" if urgency_level != "NORMALE" else "normal"),
            bg='#1a1a1a',
            fg='#ffffff',
            wraplength=400,
            justify='center'
        )
        action_label.pack(pady=(10, 5))
        
        # Countdown label
        self.countdown_label = tk.Label(
            main_frame,
            text="",
            font=("Segoe UI", 9),
            bg='#1a1a1a',
            fg='#ffa500'
        )
        self.countdown_label.pack(pady=(5, 5))
        
        # Timestamp e firma
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Frame per timestamp e firma
        footer_frame = tk.Frame(main_frame, bg='#1a1a1a')
        footer_frame.pack(pady=(0, 15))
        
        time_label = tk.Label(
            footer_frame,
            text=f"🕐 {timestamp}",
            font=("Segoe UI", 9),
            bg='#1a1a1a',
            fg='#888888'
        )
        time_label.pack()
        
        # Firma discreta
        signature_label = tk.Label(
            footer_frame,
            text="© GBochicchio",
            font=("Segoe UI", 8, "italic"),
            bg='#1a1a1a',
            fg='#555555'
        )
        signature_label.pack(pady=(2, 0))
        
        # Pulsanti
        self.crea_pulsanti_moderni(main_frame, header_color, tipo, urgency_level)
    
    def crea_barra_percentuale(self, parent, percentuale, colore, soglia_max=None):
        """Crea una barra di percentuale moderna con indicatori di soglia"""
        barra_frame = tk.Frame(parent, bg='#1a1a1a')
        barra_frame.pack(fill='x', pady=(0, 5))
        
        canvas = tk.Canvas(barra_frame, height=16, bg='#333333', highlightthickness=0)
        canvas.pack(fill='x', padx=10)
        
        # Larghezza totale disponibile
        canvas.update()
        canvas_width = 430  # Larghezza approssimativa
        
        # Barra di progresso principale
        larghezza_barra = int((percentuale / 100) * canvas_width)
        canvas.create_rectangle(2, 2, larghezza_barra, 14, fill=colore, outline="")
        
        # Indicatore soglia massima (solo per batteria carica)
        if soglia_max:
            soglia_x = int((soglia_max / 100) * canvas_width)
            canvas.create_line(soglia_x, 0, soglia_x, 16, fill='#ffffff', width=2)
            canvas.create_text(soglia_x, -8, text=f"{soglia_max}%", fill='#ffffff', 
                             font=("Segoe UI", 8), anchor='s')
        
        # Bordo della barra
        canvas.create_rectangle(1, 1, canvas_width-1, 15, outline='#555555', width=1, fill='')
    
    def crea_pulsanti_moderni(self, parent, colore_accento, tipo, urgency_level):
        """Crea pulsanti con design moderno"""
        button_frame = tk.Frame(parent, bg='#1a1a1a')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Prima riga
        top_button_frame = tk.Frame(button_frame, bg='#1a1a1a')
        top_button_frame.pack(fill='x', pady=(0, 10))
        
        # Pulsante principale - più grande se urgente
        btn_size = "bold" if urgency_level in ["IMPORTANTE", "CRITICO"] else "normal"
        btn_text = "✓ Ho capito!" if urgency_level in ["IMPORTANTE", "CRITICO"] else "✓ Ho capito"
        
        btn_principale = tk.Button(
            top_button_frame,
            text=btn_text,
            font=("Segoe UI", 12, btn_size),
            bg=colore_accento,
            fg='white',
            bd=0,
            padx=25,
            pady=12,
            cursor='hand2',
            command=self.chiudi_popup
        )
        btn_principale.pack(side='left', padx=(0, 10))
        
        # Pulsante snooze - disabilitato se critico
        if urgency_level != "CRITICO":
            btn_snooze = tk.Button(
                top_button_frame,
                text="💤 Tra 5 min",
                font=("Segoe UI", 10),
                bg='#404040',
                fg='#cccccc',
                bd=0,
                padx=20,
                pady=12,
                cursor='hand2',
                command=self.snooze_popup
            )
            btn_snooze.pack(side='left', padx=(0, 10))
        
        # Pulsante chiudi
        btn_chiudi = tk.Button(
            top_button_frame,
            text="✕",
            font=("Segoe UI", 14, "bold"),
            bg='#1a1a1a',
            fg='#666666',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.chiudi_popup
        )
        btn_chiudi.pack(side='right')
        
        # Seconda riga
        bottom_button_frame = tk.Frame(button_frame, bg='#1a1a1a')
        bottom_button_frame.pack(fill='x')
        
        # Pulsante forza chiusura - solo se non critico
        if urgency_level != "CRITICO":
            btn_forza = tk.Button(
                bottom_button_frame,
                text="🚀 Forza chiusura e continua",
                font=("Segoe UI", 10),
                bg='#666666',
                fg='white',
                bd=0,
                padx=20,
                pady=8,
                cursor='hand2',
                command=self.forza_chiusura
            )
            btn_forza.pack(side='left')
        
        # Help text
        help_text = "ESC/ENTER: chiudi"
        if urgency_level != "CRITICO":
            help_text += ", SPAZIO: forza"
        
        help_label = tk.Label(
            bottom_button_frame,
            text=help_text,
            font=("Segoe UI", 8),
            bg='#1a1a1a',
            fg='#666666'
        )
        help_label.pack(side='right', padx=(10, 0))
    
    def avvia_effetto_critico(self):
        """Effetto speciale per situazioni critiche"""
        if not self.root:
            return
        
        def pulse():
            try:
                if not self.popup_attiva or not self.animazione_attiva:
                    return
                    
                if not self.root or not self.root.winfo_exists():
                    self.animazione_attiva = False
                    return
                
                # Effetto pulsante
                for alpha in [1.0, 0.7, 1.0]:
                    if self.popup_attiva and self.root and self.root.winfo_exists():
                        self.root.attributes('-alpha', alpha)
                        self.root.update()
                        time.sleep(0.3)
                    else:
                        self.animazione_attiva = False
                        return
                
                if self.animazione_attiva and self.popup_attiva and self.root and self.root.winfo_exists():
                    self.animation_job = self.root.after(2000, pulse)
                    
            except Exception as e:
                self.animazione_attiva = False
                logger.error(f"Animazione pulse fermata: {e}")
        
        self.animazione_attiva = True
        if self.root:
            self.animation_job = self.root.after(1000, pulse)
    
    def animazione_entrata(self):
        """Animazione di entrata della finestra"""
        if not self.root:
            return
        
        self.root.attributes('-alpha', 0.0)
        
        for i in range(1, 21):
            if not self.root or not self.root.winfo_exists():
                break
            
            alpha = i / 20.0
            self.root.attributes('-alpha', alpha)
            
            if i < 20:
                self.root.update()
                time.sleep(0.02)
        
        if self.root and self.root.winfo_exists():
            self.root.attributes('-alpha', 1.0)
    
    def centra_finestra(self):
        """Centra la finestra sullo schermo"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def forza_chiusura(self):
        """Forza la chiusura del popup"""
        self.chiusura_forzata = True
        self.countdown_attivo = False
        logger.info("Popup chiuso forzatamente dall'utente")
        self.chiudi_popup()
    
    def chiudi_popup(self):
        """Chiude il popup con animazione"""
        self.animazione_attiva = False
        self.power_monitor_active = False
        self.countdown_attivo = False
        
        # Cancella tutti i job schedulati prima di chiudere
        self.cancel_scheduled_jobs()
        
        if self.root and self.root.winfo_exists():
            try:
                for i in range(10, 0, -1):
                    alpha = i / 10.0
                    self.root.attributes('-alpha', alpha)
                    self.root.update()
                    time.sleep(0.03)
            except:
                pass  # Ignora errori durante l'animazione di chiusura
        
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass  # Ignora errori durante la distruzione
        
        self.popup_attiva = False
        self.root = None
    
    def snooze_popup(self):
        """Posticipa il popup di 5 minuti"""
        logger.info("Popup posticipato di 5 minuti")
        self.chiudi_popup()

class BatteryMonitor:
    def __init__(self, soglia_min, soglia_max, intervallo):
        self.soglia_min = soglia_min
        self.soglia_max = soglia_max
        self.intervallo = intervallo
        self.ultimo_avviso_carica = 0  # Traccia l'ultima percentuale per cui abbiamo mostrato un avviso
        self.running = True
        
    def get_battery_info(self):
        """Ottiene le informazioni sulla batteria"""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                logger.error("Impossibile ottenere informazioni sulla batteria")
                return None
            return {
                "percentuale": battery.percent,
                "alimentazione": battery.power_plugged,
                "tempo_rimasto": battery.secsleft
            }
        except Exception as e:
            logger.error(f"Errore durante la lettura della batteria: {e}")
            return None
    
    def formatta_tempo_rimasto(self, secondi):
        """Formatta il tempo rimanente della batteria"""
        if secondi == -1:
            return "In carica"
        elif secondi == -2:
            return "Sconosciuto"
        else:
            ore = secondi // 3600
            minuti = (secondi % 3600) // 60
            return f"{ore}h {minuti}m"
    
    def dovrebbe_mostrare_popup_carica(self, percentuale, alimentazione):
        """Determina se dovrebbe mostrare un popup per batteria carica"""
        if not alimentazione or percentuale < self.soglia_max:
            # Reset del tracker se non in carica o sotto la soglia
            self.ultimo_avviso_carica = 0
            return False
        
        # Calcola la soglia di notifica basata sui step del 5%
        step_corrente = ((percentuale - self.soglia_max) // PROGRESSIVE_REMINDER_STEP) * PROGRESSIVE_REMINDER_STEP + self.soglia_max
        
        # Mostra popup se abbiamo raggiunto una nuova soglia del 5%
        if step_corrente > self.ultimo_avviso_carica:
            self.ultimo_avviso_carica = step_corrente
            return True
        
        return False
    
    def controlla_batteria(self):
        """Controlla lo stato della batteria e mostra popup se necessario"""
        info_batteria = self.get_battery_info()
        if info_batteria is None:
            return
        
        percentuale = info_batteria["percentuale"]
        alimentazione = info_batteria["alimentazione"]
        tempo_rimasto = self.formatta_tempo_rimasto(info_batteria["tempo_rimasto"])
        
        stato = "In carica" if alimentazione else "Non in carica"
        logger.info(f"Stato batteria: {percentuale}% - {stato} - Tempo rimasto: {tempo_rimasto}")
        
        # Controllo per batteria scarica
        if not alimentazione and percentuale <= self.soglia_min:
            logger.warning(f"Batteria sotto la soglia minima: {percentuale}%")
            popup = ModernBatteryPopup()
            popup.mostra_popup_batteria_scarica(percentuale, tempo_rimasto)
        
        # Controllo per batteria carica con promemoria progressivi
        elif self.dovrebbe_mostrare_popup_carica(percentuale, alimentazione):
            steps_over = (percentuale - self.soglia_max) // PROGRESSIVE_REMINDER_STEP
            logger.warning(f"Batteria sopra la soglia massima: {percentuale}% (step {steps_over + 1})")
            popup = ModernBatteryPopup()
            popup.mostra_popup_batteria_carica(percentuale, self.soglia_max)
    
    def run(self):
        """Esegue il monitoraggio della batteria"""
        logger.info(f"Monitor batteria avviato - Soglie: {self.soglia_min}%-{self.soglia_max}% - Intervallo: {self.intervallo}s")
        logger.info(f"Promemoria progressivi: ogni {PROGRESSIVE_REMINDER_STEP}% sopra {self.soglia_max}%")
        
        try:
            while self.running:
                self.controlla_batteria()
                time.sleep(self.intervallo)
        except KeyboardInterrupt:
            logger.info("Monitor di batteria arrestato dall'utente")
        except Exception as e:
            logger.error(f"Errore imprevisto: {e}")
    
    def stop(self):
        """Ferma il monitoraggio"""
        self.running = False

def parse_arguments():
    """Gestisce gli argomenti da linea di comando"""
    parser = argparse.ArgumentParser(description='Monitor di batteria con popup moderni')
    parser.add_argument('--min', type=int, default=DEFAULT_MIN_THRESHOLD,
                        help=f'Soglia minima percentuale (default: {DEFAULT_MIN_THRESHOLD})')
    parser.add_argument('--max', type=int, default=DEFAULT_MAX_THRESHOLD,
                        help=f'Soglia massima percentuale (default: {DEFAULT_MAX_THRESHOLD})')
    parser.add_argument('--interval', type=int, default=DEFAULT_CHECK_INTERVAL,
                        help=f'Intervallo di controllo in secondi (default: {DEFAULT_CHECK_INTERVAL})')
    parser.add_argument('--test', action='store_true',
                        help='Esegue una demo dei popup senza monitoraggio continuo')
    
    args = parser.parse_args()
    
    # Validazione
    if not 1 <= args.min <= 99:
        logger.error("La soglia minima deve essere tra 1 e 99")
        sys.exit(1)
    if not 1 <= args.max <= 100:
        logger.error("La soglia massima deve essere tra 1 e 100")
        sys.exit(1)
    if args.min >= args.max:
        logger.error("La soglia minima deve essere inferiore alla soglia massima")
        sys.exit(1)
    if args.interval < 10:
        logger.error("L'intervallo di controllo deve essere almeno 10 secondi")
        sys.exit(1)
        
    return args

def test_demo():
    """Esegue una demo completa dei popup con gestione migliorata degli errori"""
    print("\n🎬 DEMO MONITOR BATTERIA")
    print("=" * 50)
    print("Questa demo mostrerà tutti i tipi di popup possibili:")
    print("1. Batteria normale carica (80%)")
    print("2. Batteria molto carica (85% - primo promemoria)")
    print("3. Batteria sovraccarica (90% - secondo promemoria)")
    print("4. Batteria scarica normale (30%)")
    print("5. Batteria critica (10%)")
    
    input("\nPremi ENTER per iniziare la demo...")
    
    test_cases = [
        ("Batteria carica normale (80%)", lambda: ModernBatteryPopup().mostra_popup_batteria_carica(80, 80)),
        ("Primo promemoria (85%)", lambda: ModernBatteryPopup().mostra_popup_batteria_carica(85, 80)),
        ("Secondo promemoria (90%)", lambda: ModernBatteryPopup().mostra_popup_batteria_carica(90, 80)),
        ("Batteria scarica (30%)", lambda: ModernBatteryPopup().mostra_popup_batteria_scarica(30, "2h 15m")),
        ("Batteria critica (10%)", lambda: ModernBatteryPopup().mostra_popup_batteria_scarica(10, "25 minuti"))
    ]
    
    for i, (nome, test_func) in enumerate(test_cases, 1):
        print(f"\n🎯 Demo {i}/5: {nome}")
        try:
            test_func()
            print("✅ Demo completata.")
        except Exception as e:
            print(f"⚠️  Errore durante la demo: {e}")
            logger.error(f"Errore demo {i}: {e}")
        
        if i < len(test_cases):
            print("Attendi 2 secondi...")
            time.sleep(2)
    
    print("\n🎉 Demo completa! Il monitor è pronto per l'uso.")

def mostra_configurazione(args):
    """Mostra la configurazione corrente"""
    print("\n⚙️ CONFIGURAZIONE MONITOR BATTERIA")
    print("=" * 50)
    print(f"🔋 Soglia minima batteria: {args.min}%")
    print(f"⚡ Soglia massima batteria: {args.max}%")
    print(f"📊 Promemoria progressivi: ogni {PROGRESSIVE_REMINDER_STEP}% sopra {args.max}%")
    print(f"⏰ Intervallo controllo: {args.interval} secondi")
    print(f"🔌 Auto-chiusura su cambio alimentazione: {AUTO_CLOSE_ON_POWER_CHANGE}")
    print(f"⏱️ Timeout popup carica: {TIMEOUT_BATTERIA_CARICA}s")
    print(f"⏱️ Timeout popup scarica: {TIMEOUT_BATTERIA_SCARICA}s")
    print(f"⏱️ Timeout popup critica: {TIMEOUT_BATTERIA_CRITICA}s")
    print("=" * 50)
    
    # Calcola e mostra le soglie di promemoria
    print(f"\n📈 SOGLIE DI PROMEMORIA PER BATTERIA CARICA:")
    soglie = []
    for step in range(0, 4):  # Mostra fino a 4 step
        soglia = args.max + (step * PROGRESSIVE_REMINDER_STEP)
        if soglia <= 100:
            urgenza = "NORMALE" if step == 0 else "IMPORTANTE" if step == 1 else "CRITICO"
            soglie.append(f"   {soglia}% - {urgenza}")
    
    for soglia in soglie:
        print(soglia)
    
    if len(soglie) > 1:
        print(f"\n💡 Il popup apparirà quando la batteria raggiunge {args.max}%,")
        print(f"   poi di nuovo ad ogni incremento del {PROGRESSIVE_REMINDER_STEP}% se l'alimentazione")
        print(f"   rimane collegata.")

def main():
    """Funzione principale"""
    args = parse_arguments()
    
    if args.test:
        test_demo()
        return
    
    mostra_configurazione(args)
    
    # Verifica che psutil possa leggere la batteria
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            logger.error("❌ Impossibile rilevare la batteria del sistema")
            print("\n❌ ERRORE: Questo dispositivo non ha una batteria rilevabile")
            print("   Il monitor funziona solo su laptop e dispositivi portatili.")
            sys.exit(1)
        else:
            print(f"\n✅ Batteria rilevata: {battery.percent}% ({'In carica' if battery.power_plugged else 'Non in carica'})")
    except Exception as e:
        logger.error(f"❌ Errore nell'accesso alla batteria: {e}")
        sys.exit(1)
    
    print(f"\n🚀 Avvio monitor batteria...")
    print("   Premi Ctrl+C per fermare il monitoraggio")
    print("   I log vengono salvati in 'battery_monitor.log'")
    print("=" * 50)
    
    # Crea e avvia il monitor
    monitor = BatteryMonitor(args.min, args.max, args.interval)
    
    try:
        monitor.run()
    except KeyboardInterrupt:
        logger.info("🛑 Arresto richiesto dall'utente")
        monitor.stop()
        print("\n👋 Monitor batteria arrestato. Arrivederci!")
    except Exception as e:
        logger.error(f"❌ Errore critico: {e}")
        monitor.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
