"""
Bankrekening Debutade - Launcher
Start de Flask server en open de webapp in de browser
"""
import subprocess
import time
import webbrowser
import sys
import os
import urllib.request
import urllib.error

# Fix encoding voor Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_server_ready(url, max_attempts=30):
    """Check of de Flask server beschikbaar is"""
    print(">> Wachten tot server gereed is...", end="", flush=True)
    for i in range(max_attempts):
        try:
            urllib.request.urlopen(url, timeout=1)
            print(" OK")
            return True
        except (urllib.error.URLError, ConnectionRefusedError, OSError):
            time.sleep(0.5)
            print(".", end="", flush=True)
    print(" FOUT")
    return False

def main():
    print("=" * 60)
    print(">> Bankrekening Debutade - Opstarten")
    print("=" * 60)
    
    # Bepaal het werkpad (waar dit script staat)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    webapp_path = os.path.join(script_dir, "webapp.py")
    
    # Check of webapp.py bestaat
    if not os.path.exists(webapp_path):
        print(f">> FOUT: webapp.py niet gevonden in {script_dir}")
        input("Druk op Enter om af te sluiten...")
        sys.exit(1)
    
    # Start webapp.py als subprocess
    print(f">>  Start Flask server...")
    try:
        # Start als subprocess zodat we de output kunnen zien
        process = subprocess.Popen(
            [sys.executable, webapp_path],
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Wacht kort en check of het process nog draait
        time.sleep(1)
        if process.poll() is not None:
            print(">> FOUT: Server kon niet starten. Foutmelding:")
            for line in process.stdout:
                print(line.rstrip())
            input("Druk op Enter om af te sluiten...")
            sys.exit(1)
        
        # Wacht tot server beschikbaar is
        url = "http://127.0.0.1:5000"
        if check_server_ready(url):
            print(f">> Server draait op {url}")
            print(">> Opening browser...")
            
            # Open browser
            time.sleep(0.5)
            webbrowser.open(url)
            
            print("\n" + "=" * 60)
            print(">> Bankrekening Debutade is actief!")
            print("=" * 60)
            print(">> Gebruik de 'Afsluiten' knop in de webapp om te stoppen")
            print("   Of druk Ctrl+C in dit venster")
            print("=" * 60)
            
            # Wacht tot het process stopt (via /quit endpoint of Ctrl+C)
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n\n>> Stop signaal ontvangen...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(">> Geforceerd afsluiten...")
                    process.kill()
        else:
            print(">> FOUT: Server wordt niet beschikbaar binnen 15 seconden")
            print("   Check de logs voor foutmeldingen")
            process.terminate()
            input("Druk op Enter om af te sluiten...")
            sys.exit(1)
    
    except FileNotFoundError:
        print(f">> FOUT: Python niet gevonden. Zorg dat Python is geïnstalleerd.")
        input("Druk op Enter om af te sluiten...")
        sys.exit(1)
    except Exception as e:
        print(f">> FOUT: Onverwachte fout: {e}")
        input("Druk op Enter om af te sluiten...")
        sys.exit(1)
    
    print("\n>> Applicatie afgesloten")

if __name__ == "__main__":
    main()
