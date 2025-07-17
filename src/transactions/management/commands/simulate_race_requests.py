import threading
import time

import requests

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from transactions.models import Account

# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------
BASE_URL = "http://localhost:8000"
USERNAME = "user1"
PASSWORD = "testpass"
NUM_WITHDRAWS = 10      # threads de retiro por lote
NUM_DEPOSITS = 5        # threads de depósito por lote
PAUSE_BETWEEN_BATCHES = 0.05  # segundos; sube/baja si necesitas +/- presión
# ---------------------------------------------------------------------

User = get_user_model()
HEADERS: dict[str, str] = {}


# ---------------------------  Helpers  --------------------------------
def authenticate() -> None:
    """Get DRF token and set global HEADERS."""
    global HEADERS
    resp = requests.post(f"{BASE_URL}/api/token/", data={"username": USERNAME, "password": PASSWORD})
    data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
    token = data.get("token")
    if not token:
        raise RuntimeError(f"Auth failed: status={resp.status_code}, body={resp.text!r}")
    HEADERS = {"Authorization": f"Token {token}"}
    print("[INFO] Authentication successful.")


def withdraw(amount: int | float) -> None:
    requests.post(f"{BASE_URL}/api/withdraw/", json={"amount": amount}, headers=HEADERS)


def deposit(amount: int | float) -> None:
    requests.post(f"{BASE_URL}/api/deposit/", json={"amount": amount}, headers=HEADERS)


def get_balance() -> float:
    r = requests.get(f"{BASE_URL}/api/balance/", headers=HEADERS)
    return float(r.json().get("balance", 0))


def setup_test_user() -> None:
    user, _ = User.objects.get_or_create(username=USERNAME, defaults={"password": make_password(PASSWORD)})
    Token.objects.get_or_create(user=user)
    account, created = Account.objects.get_or_create(user=user)
    if created:
        account.balance = 100
        account.save()
        print("[INFO] Created test account with initial balance = 100")


# ---------------------------  Command  --------------------------------
class Command(BaseCommand):
    help = "Stress-test concurrent deposit/withdraw endpoints and flag negative balance"

    def handle(self, *args, **kwargs) -> None:
        setup_test_user()
        authenticate()

        stop_event = threading.Event()
        start_time = time.time()

        # --- Monitor thread ---
        def monitor_balance() -> None:
            checks = 0
            while not stop_event.is_set():
                bal = get_balance()
                checks += 1
                if checks % 1000 == 0:
                    elapsed = time.time() - start_time
                    print(f"Balance checks: {checks}  |  elapsed: {elapsed:.1f}s  |  current balance: {bal}")
                if bal < 0:
                    elapsed = time.time() - start_time
                    print(
                        f"\033[91m[ERROR] Negative balance detected: {bal} "
                        f"after {checks} checks (elapsed {elapsed:.1f}s)\033[0m"
                    )
                    stop_event.set()
                time.sleep(0.01)  # frecuencia de chequeo

        threading.Thread(target=monitor_balance, daemon=True).start()

        # --- Producer loop ---
        print("Starting stress loop (Ctrl-C to stop)…")
        batches = 0
        try:
            while not stop_event.is_set():
                threads: list[threading.Thread] = []
                for _ in range(NUM_WITHDRAWS):
                    threads.append(threading.Thread(target=withdraw, args=(60,)))
                for _ in range(NUM_DEPOSITS):
                    threads.append(threading.Thread(target=deposit, args=(50,)))

                for t in threads:
                    t.start()
                for t in threads:
                    t.join()  # espera a que este lote concreto termine

                batches += 1
                if batches % 100 == 0:
                    print(f"Completed {batches} batches …")

                time.sleep(PAUSE_BETWEEN_BATCHES)  # alivia un poco la BD
        except KeyboardInterrupt:
            print("\n[INFO] Interrupted by user.")
            stop_event.set()

        total_elapsed = time.time() - start_time
        print(f"Total elapsed time: {total_elapsed:.1f}s")
