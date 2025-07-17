# Welcome to Python Editor integrated with SORBA. Use sde["ASSET.GROUP.TAG"] to read or write tags. 
# Set the execution control: On Start, Cyclic, On Stop, Module, On Schedule, On Trigger and Callable.
# Define global variables using glb.add(name=value,...),access as glb.name.Also use global keyword to share variables, functions,lib.
# For debugging, use debug(*args) and visualize the results in the Debug tab. To monitor runtime, check Statistics tab.
# Look for built-in script functions and modules like timer, counter, track, cyclic_list, and time_counter (RepeatTimer,Heartbeat, Async).
# To import Python modules outside of Script-Engine, add to the “On Start” script: import sys; sys.path.append ('new path')
# Enter your Python code here.For more information related with quality,channel,glb, packages installation, please refer to the help file.
import time
import streamlit as st
from sorba_sdk.core.data_sdk.data_sdk import SorbaData
from sorba_sdk.core.auth_sdk.app_authenticator import AppAuthenticator

# Set page configuration
namespace = "SorbaDataMonitor"
rt_refresh_time = 1
hist_refresh_time = 2
layout = "wide"

# Page title and layout
st.set_page_config(page_title=namespace, layout=layout)

# Save the sorba_data instance in the Streamlit session state.
# The SorbaData object helps us read and write real-time and historical data. It may store some tag metadata 
# in memory, so we need to save it in Streamlit's session state to avoid making continuous queries to the Sorba APIs.
if "sorba_data" not in st.session_state:
    st.session_state.sorba_data = SorbaData(namespace)

# Save the app_authenticator instance in the Streamlit session state.
# The AppAuthenticator object helps us authenticate users with the Sorba Identity service, so app users
# can access this app only if they are authenticated. If you omit this step, all users will be able to access this app
# causing a security risk.
if "app_authenticator" not in st.session_state:
    st.session_state.app_authenticator = AppAuthenticator(namespace)

# Only show the page content if the user is authenticated, otherwise show the login page
if not st.session_state.app_authenticator.authenticated:
    st.session_state.app_authenticator.login_page(layout=layout)
else:

    # Include a header with the user's full name and a log out button
    headers = st.columns(5)
    with headers[3]:
        st.write(f"Hello, {st.session_state.app_authenticator.user_full_name}!")
    with headers[4]:
        if st.button("Log out", type="primary"):
            st.session_state.app_authenticator.logout()

    st.title("Sorba Data Monitor")

    st.sidebar.write("Display Settings")
    # We let the user define the amount of historical data he wants to plot
    hist_len = int(st.sidebar.slider("Display History Lenght (Seconds)", min_value=10, max_value=3600, value=60, step=1))

    def load_tags(refresh: bool):
        if refresh:
            st.session_state.sorba_data.refresh_cache()
        options = []
        options_meta = {}
        if st.session_state.sorba_data.cache is not None:
            for abs_path, meta in st.session_state.sorba_data.cache.items():
                options.append(abs_path)
                options_meta[abs_path] = (abs_path, abs_path.split(".")[-1].capitalize(), meta["unit"])

        return options, options_meta

    @st.experimental_fragment(run_every=rt_refresh_time)
    def rt_data_updater():
        if "tags_meta" in st.session_state:
            tags = st.session_state.tags_meta
            if len(tags) > 0:
                tag_paths = [t[0] for t in tags]
                values = st.session_state.sorba_data.rt_read(tag_paths, as_dict=False)
                prev_values = (st.session_state.prev_values
                            if "prev_values" in st.session_state and len(values) == len(st.session_state.prev_values)
                            else values)

                delta = [(v - pv if v is not None and pv is not None else None) for v, pv in zip(values, prev_values)]

                columns = st.columns(len(tags))
                for i, column in enumerate(columns):
                    display_name = tags[i][1]
                    unit = tags[i][2] if values[i] is not None else ""
                    val = "{:.2f}".format(values[i]) if values[i] is not None else "NULL"
                    delt = "{:.2f}".format(delta[i]) if delta[i] is not None else ""
                    column.metric(display_name, f"{val} {unit}", f"{delt} {unit}")

                st.session_state.prev_values = values

    @st.experimental_fragment(run_every=hist_refresh_time)
    def hist_data_updater():
        if "tags_meta" in st.session_state:
            tags = st.session_state.tags_meta
            if len(tags) > 0:
                tag_paths = [t[0] for t in tags]
                now = int(time.time() * 1000)
                start = now - hist_len * 1000
                end = now
                df = st.session_state.sorba_data.hist_read(
                    tag_paths,
                    start_time_ms=start,
                    end_time_ms=end,
                    as_df=True,
                    as_timestamp=True
                )
                df.rename(columns={t[0]: f"{t[1]} {t[2]}" for t in tags}, inplace=True)
                st.line_chart(df)

    with st.container():

        if "initial_loaded" not in st.session_state:
            refresh = True
            st.session_state.initial_loaded = 1
        else:
            refresh = st.button("Refresh Tags")
        options, options_meta = load_tags(refresh)

        selected_paths = st.multiselect("Select tags to monitor", options)
        st.session_state.tags_meta = [options_meta[sp] for sp in selected_paths]

        st.header("Real Time")
        rt_data_updater()
        st.header("Historical")
        hist_data_updater()
