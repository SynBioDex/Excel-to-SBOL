#!/usr/bin/env python3
"""
app.py - pywebview host for Excel2SBOL
Serves web/index.html in a native OS window and exposes a Python API
to the frontend via window.pywebview.api.
"""

import os
import sys
import json
import logging
import threading
from datetime import datetime

import webview
import requests
import pandas as pd
import excel2sbol as conf

from generator import generate
from generator.sheet_definitions import TEMPLATE_CONFIGS

# ------------------------------------------------------------------ #
# Paths & constants                                                    #
# ------------------------------------------------------------------ #

_HERE = os.path.dirname(os.path.abspath(__file__))

HISTORY_FILE = os.path.join(_HERE, "user_history.json")


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def resource_path(relative_path):
    base = getattr(sys, '_MEIPASS', _HERE)
    return os.path.join(base, relative_path)


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {"domains": [], "emails": []}


def save_history(domain, email):
    history = load_history()
    if domain and domain not in history["domains"]:
        history["domains"].append(domain)
    if email and email not in history["emails"]:
        history["emails"].append(email)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def _error_text(exc: Exception) -> str:
    """Human-readable message for the GUI.

    str(KeyError("x")) renders with quotes ("'x'"), so single-arg exceptions use
    args[0]. OSError is different: its args are (errno, strerror), so args[0]
    reports a bare number (a Windows "Access is denied" surfaced as "13") and
    discards the operation and the paths. Report those in full.
    """
    if isinstance(exc, OSError):
        where = " -> ".join(p for p in (exc.filename, exc.filename2) if p)
        msg = f"{type(exc).__name__}: {exc.strerror or exc}"
        return f"{msg} ({where})" if where else msg
    return (str(exc.args[0]) if exc.args else str(exc)) or type(exc).__name__


class _WarningCollector(logging.Handler):
    """Collects WARNING+ log records emitted during a conversion so the GUI can
    show them. The converter/compiler report skipped rows, blank ids, etc. via
    logging.warning(), which otherwise only reaches the terminal. Attach around
    the converter call, then read `.messages`.
    """

    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.messages = []

    def emit(self, record):
        try:
            self.messages.append(self.format(record))
        except Exception:
            pass


# ------------------------------------------------------------------ #
# API                                                                  #
# ------------------------------------------------------------------ #

class Api:
    """Exposed to JavaScript as window.pywebview.api."""

    def __init__(self):
        self._window = None
        self._progress = {"finished": False, "success": False, "message": "Ready"}
        self._sc_progress = {"finished": False, "success": False, "message": "Ready"}

    def set_window(self, window):
        self._window = window

    # ------------------------------------------------------------------ #
    # File / folder dialogs                                                #
    # ------------------------------------------------------------------ #

    def pick_file(self):
        if not self._window:
            return None
        try:
            result = self._window.create_file_dialog(
                webview.FileDialog.OPEN,
                file_types=('Excel files (*.xlsx;*.xlsm)',)
            )
            if result:
                return str(result[0]) if isinstance(result, (list, tuple)) else str(result)
            return None
        except Exception as e:
            print(f"[pick_file] Error: {e}")
            return None

    def pick_folder(self):
        if not self._window:
            return None
        try:
            result = self._window.create_file_dialog(webview.FileDialog.FOLDER)
            if result:
                return str(result[0]) if isinstance(result, (list, tuple)) else str(result)
            return None
        except Exception as e:
            print(f"[pick_folder] Error: {e}")
            return None

    # ------------------------------------------------------------------ #
    # Converter - Excel metadata                                           #
    # ------------------------------------------------------------------ #

    def get_excel_metadata(self, file_path):
        """Read SBOL version, domain, and email from the selected Excel file."""
        result: dict = {"sbol_version": None, "domain": None, "email": None}
        try:
            df_init = pd.read_excel(file_path, sheet_name="Init", header=None, usecols="B", nrows=1)
            result["sbol_version"] = int(df_init.iloc[0, 0])
        except Exception:
            pass
        try:
            # The welcome sheet stores fields as a label (col B) -> value (col C)
            # table. Read by label rather than a fixed row index: the old code used
            # hard-coded iloc positions (domain iloc[15] with nrows=13 -> always
            # IndexError -> None; email iloc[7] -> the Institution row), both wrong.
            df_w = pd.read_excel(file_path, sheet_name="welcome", header=None, usecols="B,C")
            labels = df_w.iloc[:, 0].astype(str).str.strip()

            def _welcome_field(label):
                match = df_w[labels == label]
                if match.empty:
                    return None
                value = match.iloc[0, 1]
                return None if pd.isna(value) else str(value)

            domain = _welcome_field("Domain")
            if domain:
                result["domain"] = domain.rstrip("/")
            email = _welcome_field("Email")
            if email:
                result["email"] = email
        except Exception:
            pass
        return json.dumps(result)

    # ------------------------------------------------------------------ #
    # Converter - history                                                  #
    # ------------------------------------------------------------------ #

    def get_history(self):
        return json.dumps(load_history())

    # ------------------------------------------------------------------ #
    # Converter - run                                                      #
    # ------------------------------------------------------------------ #

    def run_conversion(self, config_json):
        config = json.loads(config_json)
        self._progress = {"finished": False, "success": False, "message": "Starting..."}
        t = threading.Thread(target=self._do_conversion, args=(config,), daemon=True)
        t.start()
        return "ok"

    def _do_conversion(self, config):
        # Capture the converter's logging.warning() output (skipped rows, blank
        # ids, unresolved lookups) so the GUI can report it, not just the terminal.
        collector = _WarningCollector()
        collector.setFormatter(logging.Formatter("%(message)s"))
        root = logging.getLogger()
        root.addHandler(collector)
        prev_level = root.level
        if not root.isEnabledFor(logging.WARNING):
            root.setLevel(logging.WARNING)
        try:
            file_path = config["file_path"]
            sbol_version = int(config["sbol_version"])
            use_signin = config.get("use_signin", False)
            domain = config.get("domain", "").rstrip("/")
            email = config.get("email", "")
            password = config.get("password", "")

            if use_signin:
                self._progress["message"] = "Validating domain..."
                for attempt in range(1, 4):
                    try:
                        requests.get(domain, timeout=10)
                        break
                    except requests.exceptions.RequestException:
                        if attempt == 3:
                            raise Exception("Invalid domain after 3 attempts.")

                self._progress["message"] = "Signing in..."
                for attempt in range(1, 4):
                    resp = requests.post(
                        f"{domain}/login",
                        headers={"Accept": "plain/text"},
                        data={"email": email, "password": password},
                        timeout=10
                    )
                    if resp.status_code == 200:
                        break
                    if attempt == 3:
                        raise Exception("Incorrect email or password.")

            dt = datetime.now().strftime("%y.%m.%d.%H.%M.%S")
            base = os.path.splitext(os.path.basename(file_path))[0]
            out = os.path.join(os.path.dirname(file_path), f"{base}_{dt}.xml")

            self._progress["message"] = "Converting..."

            if use_signin:
                conf.converter(file_path, out, sbol_version=sbol_version,
                               username=email, password=password, url=domain)
                save_history(domain, email)
            else:
                conf.converter(file_path, out, sbol_version=sbol_version)

            self._progress.update({
                "finished": True, "success": True,
                "message": f"Output saved to: {out}",
                "warnings": collector.messages,
            })
        except Exception as e:
            self._progress.update({
                "finished": True, "success": False,
                "message": _error_text(e),
                "warnings": collector.messages,
            })
        finally:
            root.removeHandler(collector)
            root.setLevel(prev_level)

    def get_progress(self):
        return json.dumps(self._progress)

    # ------------------------------------------------------------------ #
    # Spreadsheet Creator                                                  #
    # ------------------------------------------------------------------ #

    def generate_spreadsheet(self, config_json):
        """
        config = {
          template_type: "resources"|"strains"|"sample_design"|"assay",
          selected_parts: [...],   # Resources only
          output_folder: "/path",
          metadata: {
            library_name, collection_id, version, author, email, lab,
            institution, description, pubmed_id, sbol_version,
            domain, master_collection
          }
        }
        """
        config = json.loads(config_json)
        self._sc_progress = {"finished": False, "success": False, "message": "Starting..."}
        t = threading.Thread(target=self._do_generate, args=(config,), daemon=True)
        t.start()
        return "ok"

    def _do_generate(self, config):
        try:
            template_type = config["template_type"]

            gen_config = {
                "template_type":      template_type,
                "output_folder":      config["output_folder"],
                "metadata":           config["metadata"],
                "user_custom_sheets": config.get("custom_sheets", []),
                "sheet_order":        config.get("sheet_order", []),
                "column_orders":      config.get("column_orders", {}),  # F4
            }
            if template_type in ("resources", "custom"):
                gen_config["selected_sheets"] = config.get("selected_parts", [])

            out_path = generate(
                gen_config,
                progress_cb=lambda msg: self._sc_progress.update({"message": msg}),
            )
            out_filename = os.path.basename(out_path)

            self._sc_progress.update({
                "finished": True, "success": True,
                "message": f"Saved to: {out_path}",
                "filename": out_filename,
            })
        except Exception as e:
            self._sc_progress.update({
                "finished": True, "success": False,
                "message": _error_text(e)
            })

    def get_sc_progress(self):
        return json.dumps(self._sc_progress)

    def get_sheet_catalog(self, template_type="resources"):
        """Return grouped sheet metadata for dynamic checkbox rendering."""
        if template_type == "custom":
            # All unique sheets from every template config, nothing pre-checked.
            # Sheets flagged ui_selectable=False (e.g. signal) are excluded from
            # the custom catalog.
            seen = set()
            sheets_to_show = []
            for config_sheets in TEMPLATE_CONFIGS.values():
                for sdef in config_sheets:
                    if sdef.name not in seen and getattr(sdef, "ui_selectable", True):
                        seen.add(sdef.name)
                        sheets_to_show.append(sdef)
            use_default = False
        else:
            sheets_to_show = TEMPLATE_CONFIGS.get(template_type, TEMPLATE_CONFIGS["resources"])
            use_default = True

        groups = {}
        for sdef in sheets_to_show:
            group = sdef.ui_group or "Other"
            if group not in groups:
                groups[group] = []
            groups[group].append({
                "name":            sdef.name,
                "display_name":    sdef.display_name,
                "hint":            sdef.ui_hint,
                "default_checked": sdef.ui_default_checked if use_default else False,
                # F4: column names (in default order) for the reorder popup.
                "columns":         [c.name for c in sdef.columns],
            })
        result = [{"group": g, "sheets": s} for g, s in groups.items()]
        return json.dumps(result)


# ------------------------------------------------------------------ #
# Entry point                                                          #
# ------------------------------------------------------------------ #

def main():
    api = Api()
    web_dir = resource_path("web")
    icon_path = resource_path(os.path.join("web", "E2S_Icon.png"))

    window = webview.create_window(
        "Excel2SBOL",
        url=os.path.join(web_dir, "index.html"),
        width=620,
        height=800,
        min_size=(500, 600),
        text_select=False,
        js_api=api
    )

    api.set_window(window)

    def set_app_icon():
        if sys.platform == "darwin":
            try:
                from AppKit import NSApplication, NSImage
                ns_app = NSApplication.sharedApplication()
                icon = NSImage.alloc().initByReferencingFile_(icon_path)
                ns_app.setApplicationIconImage_(icon)
            except Exception:
                pass
        elif sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Excel2SBOL.App")
            except Exception:
                pass

    webview.start(func=set_app_icon, debug=False)


if __name__ == "__main__":
    main()
