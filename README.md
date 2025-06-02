# 🔋 Battery Monitor Pro

Un monitor di batteria intelligente e moderno per laptop con popup eleganti e notifiche progressive per preservare la salute della batteria.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)
![Development](https://img.shields.io/badge/macOS%20%7C%20Linux-planned-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Caratteristiche

### 🎯 Monitoraggio Intelligente
- **Soglie personalizzabili** per batteria scarica e carica
- **Promemoria progressivi** ogni 5% sopra la soglia massima per evitare il sovraccarico
- **Rilevamento automatico** del cambio di alimentazione con chiusura intelligente dei popup
- **Logging completo** di tutti gli eventi

### 🎨 Interface Moderna
- **Popup eleganti** con design moderno e dark theme
- **Animazioni fluide** di entrata e uscita
- **Effetti speciali** per situazioni critiche (pulsazioni e trasparenza)
- **Countdown automatico** per la chiusura dei popup
- **Indicatori visivi** di urgenza con colori dinamici

### ⚡ Gestione Avanzata
- **Auto-chiusura intelligente** quando si collega/scollega l'alimentazione
- **Timeout differenziati** basati sulla criticità della situazione
- **Modalità snooze** per posticipare le notifiche
- **Scorciatoie da tastiera** per controllo rapido

## 🖥️ Compatibilità

### ✅ **Supporto Completo**
- **Windows 10/11** - Completamente testato e ottimizzato
- Tutte le funzionalità disponibili
- Design ottimizzato per l'ecosistema Windows

### 🚧 **Sviluppo Futuro**
- **macOS** - Pianificato per versioni future
- **Linux** - In roadmap di sviluppo
- Contribuzioni per altri sistemi operativi sono benvenute!

> **Nota**: Il software utilizza librerie Python standard multipiattaforma (`psutil`, `tkinter`), ma l'interfaccia utente e alcuni effetti sono attualmente ottimizzati specificamente per Windows.

### Prerequisiti
```bash
pip install psutil tkinter
```

### Download
```bash
git clone https://github.com/GBochicchio/battery-monitor-pro.git
cd battery-monitor-pro
```

## 📖 Utilizzo

### Avvio Rapido
```bash
python battery-monitor-pro.py
```

### Configurazione Personalizzata
```bash
# Soglia minima 30%, massima 85%, controllo ogni 2 minuti
python battery-monitor-pro.py --min 30 --max 85 --interval 120
```

### Demo Completa
```bash
# Testa tutti i tipi di popup senza monitoraggio continuo
python battery-monitor-pro.py --test
```

## ⚙️ Parametri di Configurazione

| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| `--min` | 20 | Soglia minima batteria (%) |
| `--max` | 80 | Soglia massima batteria (%) |
| `--interval` | 300 | Intervallo controllo (secondi) |
| `--test` | - | Modalità demo |

### Esempio di Configurazioni Comuni

**Uso conservativo (massima durata batteria):**
```bash
python battery-monitor-pro.py --min 30 --max 70
```

**Uso bilanciato (raccomandato):**
```bash
python battery-monitor-pro.py --min 40 --max 80
```

**Uso intensivo:**
```bash
python battery-monitor-pro.py --min 20 --max 90
```

## 🎯 Come Funziona

### Sistema di Promemoria Progressivi
Il monitor utilizza un sistema intelligente di notifiche progressive:

1. **Prima notifica** al raggiungimento della soglia massima (es. 80%)
2. **Promemoria crescenti** ogni 5% aggiuntivi (85%, 90%, 95%)
3. **Urgenza crescente** con colori e messaggi più intensi

### Tipi di Popup

#### 🔋 Batteria Scarica
- **Normale** (20-40%): Notifica standard
- **Urgente** (10-20%): Colori arancioni e testo enfatizzato  
- **Critico** (<10%): Rosso lampeggiante, nessun auto-close

#### ⚡ Batteria Carica
- **Normale** (soglia raggiunta): Verde, promemoria gentile
- **Importante** (+5% sopra soglia): Arancione, tono più insistente
- **Critico** (+10% sopra soglia): Rosso, avviso urgente

### Auto-Chiusura Intelligente
I popup si chiudono automaticamente quando:
- Si collega l'alimentazione (per popup batteria scarica)
- Si scollega l'alimentazione (per popup batteria carica)
- Scade il timeout configurato
- L'utente forza la chiusura

## 🎮 Controlli

### Scorciatoie da Tastiera
- **ESC** / **ENTER**: Chiudi popup
- **SPAZIO**: Forza chiusura (ignora timeout)

### Pulsanti
- **✓ Ho capito**: Chiusura normale
- **💤 Tra 5 min**: Posticipa notifica (snooze)
- **🚀 Forza chiusura**: Chiudi ignorando i controlli
- **✕**: Chiudi popup

## 📊 Logging

Tutti gli eventi vengono registrati in `battery_monitor.log`:
```
2025-06-02 14:30:15 - INFO - Monitor batteria avviato - Soglie: 40%-80%
2025-06-02 14:35:20 - INFO - Stato batteria: 78% - In carica
2025-06-02 14:40:25 - WARNING - Batteria sopra la soglia massima: 82%
2025-06-02 14:40:30 - INFO - Popup chiuso automaticamente: 🔋 Alimentazione scollegata
```

## 🛡️ Preservazione della Batteria

### Perché Usare Battery Monitor Pro?

Le batterie agli ioni di litio moderne durano di più quando:
- Non vengono completamente scaricate (evitare <20%)
- Non vengono sempre caricate al 100% (ottimale 80-85%)
- Non rimangono collegate costantemente al caricatore

### Benefici
- **Aumenta la durata** della batteria fino al 50%
- **Riduce il degrado** chimico delle celle
- **Migliora le performance** a lungo termine
- **Risparmio economico** evitando sostituzioni precoci

## 🔧 Configurazione Avanzata

### Personalizzazione Timeout
Modifica le costanti nel codice per timeout personalizzati:
```python
TIMEOUT_BATTERIA_CARICA = 30      # Popup batteria carica
TIMEOUT_BATTERIA_SCARICA = 90     # Popup batteria scarica  
TIMEOUT_BATTERIA_CRITICA = 0      # Popup critico (nessun timeout)
```

### Intervallo Promemoria
```python
PROGRESSIVE_REMINDER_STEP = 5     # Promemoria ogni 5%
```

### Auto-chiusura
```python
AUTO_CLOSE_ON_POWER_CHANGE = True  # Chiudi su cambio alimentazione
POWER_CHECK_INTERVAL = 2           # Controlla ogni 2 secondi
```

## 🚦 Avvio Automatico

### Windows (Task Scheduler) - Raccomandato
1. Apri Task Scheduler (`taskschd.msc`)
2. Crea attività base
3. Trigger: "All'avvio"
4. Azione: Avvia programma
5. Programma: `python`
6. Argomenti: `C:\path\to\battery-monitor-pro.py`

## 🤝 Contribuire

Le contribuzioni sono benvenute! Per favore:

1. Fai un fork del repository
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

### Idee per Contribuzioni
- 🍎 **Supporto macOS** con font e stili nativi
- 🐧 **Supporto Linux** con adattamenti per diversi DE
- 🌐 Supporto per più lingue
- 📱 Integrazione con notifiche sistema
- 📊 Grafici storici della batteria
- 🎨 Temi personalizzabili
- 🔊 Notifiche audio
- ☁️ Sincronizzazione cloud delle impostazioni

## 📋 TODO

- [ ] 🍎 Supporto nativo per macOS
- [ ] 🐧 Supporto per Linux (Ubuntu, Fedora, Arch)
- [ ] Interfaccia grafica per configurazione
- [ ] Statistiche uso batteria
- [ ] Profili utente multipli
- [ ] Integrazione con Windows Battery Report
- [ ] Modalità gaming (pause monitoring)
- [ ] API REST per controllo remoto

## 🐛 Risoluzione Problemi

### Il monitor non rileva la batteria
**Soluzione**: Verificare che il dispositivo abbia una batteria e che psutil abbia i permessi necessari.

### Popup non appaiono
**Soluzione**: Controllare che tkinter sia installato e che il display sia disponibile.

### Errori di permessi
**Soluzione**: Su Linux, potrebbe essere necessario aggiungere l'utente al gruppo appropriato.

### Log non vengono creati
**Soluzione**: Verificare i permessi di scrittura nella directory di esecuzione.

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file `LICENSE` per dettagli.

## 👨‍💻 Autore

**GBochicchio** - *Sviluppo e mantenimento* - [GitHub](https://github.com/GBochicchio)

## 🙏 Ringraziamenti

- **psutil** per il monitoraggio sistema
- **tkinter** per l'interfaccia grafica
- Community Python per ispirazione e supporto

---

<p align="center">
  <strong>💡 Preserva la tua batteria, preserva il pianeta! 🌱</strong>
</p>

<p align="center">
  Se questo progetto ti è utile, considera di dargli una ⭐ su GitHub!
</p>
