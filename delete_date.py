import subprocess
import os
import shutil
import signal
import sys

# Dizionari per i messaggi
MESSAGES = {
    "it": {
        "not_root": "❌ Devi eseguire questo script come root.",
        "install_pv": "ℹ️  Installazione di 'pv' in corso...",
        "partitions": "📋 Partizioni disponibili:\n",
        "insert_device": "✏️  Inserisci il nome del device da cancellare (es. sdb1): ",
        "not_exist": "❌ Il dispositivo {device} non esiste.",
        "mounted": "❌ Il dispositivo {device} è montato. Smontalo prima.",
        "confirm": "\n⚠️  ATTENZIONE: Tutti i dati su {device} saranno IRREVERSIBILMENTE CANCELLATI!\n❓ Vuoi procedere? (s/n): ",
        "cancelled": "❌ Operazione annullata.",
        "error_size": "❌ Errore nel leggere la dimensione del dispositivo.",
        "start_wipe": "\n🚀 Inizio scrittura zeri su {device} ({size} MB)...\n",
        "done": "\n✅ Scrittura completata su {device}!",
    },
    "en": {
        "not_root": "❌ You must run this script as root.",
        "install_pv": "ℹ️  Installing 'pv'...",
        "partitions": "📋 Available partitions:\n",
        "insert_device": "✏️  Enter the name of the device to erase (e.g., sdb1): ",
        "not_exist": "❌ The device {device} does not exist.",
        "mounted": "❌ The device {device} is mounted. Please unmount it first.",
        "confirm": "\n⚠️  WARNING: All data on {device} will be IRREVERSIBLY ERASED!\n❓ Do you want to proceed? (y/n): ",
        "cancelled": "❌ Operation cancelled.",
        "error_size": "❌ Error reading device size.",
        "start_wipe": "\n🚀 Starting zero write on {device} ({size} MB)...\n",
        "done": "\n✅ Wipe completed on {device}!",
    }
}

# Blocco Ctrl+C e Ctrl+Z
def block_signals():
    signal.signal(signal.SIGINT, signal.SIG_IGN)   # Ignora Ctrl+C
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)  # Ignora Ctrl+Z

def choose_language():
    print("🌐 Select language / Seleziona la lingua:\n")
    print("1) Italiano")
    print("2) English\n")

    choice = input("👉 ").strip()
    if choice == "1":
        return "it"
    elif choice == "2":
        return "en"
    else:
        print("⚠️ Default: English\n")
        return "en"

def list_partitions(lang):
    print(MESSAGES[lang]["partitions"])
    subprocess.run(["lsblk", "-o", "NAME,SIZE,FSTYPE,MOUNTPOINT"])
    print()

def is_device_mounted(device):
    result = subprocess.run(["mount"], stdout=subprocess.PIPE, text=True)
    return device in result.stdout

def get_device_size_bytes(device, lang):
    try:
        output = subprocess.check_output(["blockdev", "--getsize64", device], text=True)
        return int(output.strip())
    except subprocess.CalledProcessError:
        print(MESSAGES[lang]["error_size"])
        return None

def main():
    block_signals()  # Disabilita Ctrl+C e Ctrl+Z
    lang = choose_language()
    msg = MESSAGES[lang]

    if os.geteuid() != 0:
        print(msg["not_root"])
        return

    if not shutil.which("pv"):
        print(msg["install_pv"])
        subprocess.run(["apt", "update"])
        subprocess.run(["apt", "install", "-y", "pv"])

    list_partitions(lang)

    part = input(msg["insert_device"]).strip()
    device = f"/dev/{part}"

    if not os.path.exists(device):
        print(msg["not_exist"].format(device=device))
        return

    if is_device_mounted(device):
        print(msg["mounted"].format(device=device))
        return

    conferma = input(msg["confirm"].format(device=device)).strip().lower()
    if conferma not in ['s', 'y']:  # accetta 's' (si) e 'y' (yes)
        print(msg["cancelled"])
        return

    size_bytes = get_device_size_bytes(device, lang)
    if size_bytes is None:
        return

    size_mb = size_bytes // (1024 * 1024)
    print(msg["start_wipe"].format(device=device, size=size_mb))

    dd_command = f"dd if=/dev/zero bs=1M count={size_mb} 2>/dev/null | pv -s {size_mb}M > {device}"
    subprocess.run(dd_command, shell=True, executable="/bin/bash")

    print(msg["done"].format(device=device))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Anche se per sicurezza lo gestiamo qui
        print("\n⚠️ Interruzione bloccata. Lo script continua...")
        main()
