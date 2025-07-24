# Welcome to Python Editor integrated with SORBA. Use sde["ASSET.GROUP.TAG"] to read or write tags. 
# Set the execution control: On Start, Cyclic, On Stop, Module, On Schedule, On Trigger and Callable.
# Define global variables using glb.add(name=value,...),access as glb.name.Also use global keyword to share variables, functions,lib.
# For debugging, use debug(*args) and visualize the results in the Debug tab. To monitor runtime, check Statistics tab.
# Look for built-in script functions and modules like timer, counter, track, cyclic_list, and time_counter (RepeatTimer,Heartbeat, Async).
# To import Python modules outside of Script-Engine, add to the “On Start” script: import sys; sys.path.append ('new path')
# Enter your Python code here.For more information related with quality,channel,glb, packages installation, please refer to the help file.

from playwright.sync_api import sync_playwright
import time
from queue import Queue 

global sync_playwright, Callweb, data

data = Queue()  # to be used by regular cyclic script

def Callweb():
    global sync_playwright, data
    # Target URL
    URL = "https://sae.mec.gub.uy/sae/agendarReserva/Paso1.xhtml?e=9&a=7&r=13"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=100)
        page = browser.new_page()

        try:
            page.goto(URL, wait_until="domcontentloaded")

            # Click on the "Elegir día y hora ▶" button
            page.click("input#form\\:botonElegirHora")

            # Wait for content to load
            time.sleep(3)

            # Check if warning message is present
            warning = page.query_selector("p.ui-messages-warn-title")
            if warning is None:
                debug("✔ Hay cupos disponibles")
                data.put((1,"Hay cupos disponibles"))
                debug(f"✅ Sent to {destination_tag}: {sde[destination_tag]}")
            else:
                debug("✖ No hay cupos disponibles")
                data.put((0,"No hay cupos disponibles"))
                debug(f"📭 Sent to {destination_tag}: {sde[destination_tag]}")

        except Exception as e:
            debug("🚨 Ocurrió un error:", str(e))

        finally:
            browser.close()
