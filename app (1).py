import streamlit as st
from DisasterResponseAI import DisasterResponseAI, DisasterZone

def main():
    st.title("Disaster Response AI Coordinator")

    if 'ai' not in st.session_state:
        st.session_state.ai = DisasterResponseAI()
    if 'zones' not in st.session_state:
        st.session_state.zones = []

    st.header("Add a New Zone")
    with st.form(key="add_zone_form"):
        zone_name = st.text_input("Enter zone name:")
        location = st.text_input("Enter location (city, country):")
        population = st.number_input("Enter population:", min_value=0, step=1)
        submit_button = st.form_submit_button(label="Add Zone")
        if submit_button:
            coords = st.session_state.ai.geocode_location(location)
            if coords:
                zone = DisasterZone(zone_name, coords['lat'], coords['lng'], population)
                st.session_state.zones.append(zone)
                st.session_state.ai.add_zone(zone)
                st.success(f"Zone {zone_name} added successfully!")
            else:
                st.error("Failed to geocode location. Zone not added.")

    st.header("Assess Disaster Risk")
    disaster_type = st.selectbox("Select disaster type", ['flood', 'hurricane', 'earthquake', 'wildfire'])
    if st.button("Assess Risk"):
        if not st.session_state.zones:
            st.warning("No zones added yet. Please add zones first.")
        else:
            for zone in st.session_state.zones:
                zone.risk_level = st.session_state.ai.assess_risk(zone, disaster_type)
                st.write(f"{zone.name}: Risk level {zone.risk_level:.2f}")

    st.header("Allocate Resources")
    if st.button("Allocate Resources"):
        if not st.session_state.zones:
            st.warning("No zones added yet. Please add zones first.")
        else:
            st.session_state.ai.allocate_resources(disaster_type)
            for zone in st.session_state.zones:
                st.write(f"{zone.name}: Allocated resources {dict(zone.resources)}")

    st.header("Recommend Actions")
    if st.button("Recommend Actions"):
        if not st.session_state.zones:
            st.warning("No zones added yet. Please add zones first.")
        else:
            actions = st.session_state.ai.recommend_actions(disaster_type)
            for action in actions:
                st.write(action)

    st.header("Find Safest Route Between Zones")
    if len(st.session_state.zones) < 2:
        st.warning("Need at least two zones to find a route.")
    else:
        start_zone_name = st.selectbox("Select starting zone", [zone.name for zone in st.session_state.zones])
        end_zone_name = st.selectbox("Select destination zone", [zone.name for zone in st.session_state.zones])
        if st.button("Find Safest Route"):
            start_zone = next((z for z in st.session_state.zones if z.name == start_zone_name), None)
            end_zone = next((z for z in st.session_state.zones if z.name == end_zone_name), None)
            if start_zone and end_zone:
                route = st.session_state.ai.heuristic_search_safest_route(start_zone, end_zone)
                if route:
                    st.write("Safest route:")
                    for zone in route:
                        st.write(f"  {zone.name} (Risk: {zone.risk_level:.2f})")
                else:
                    st.write("No safe route found.")
            else:
                st.warning("Invalid zone names.")

if __name__ == "__main__":
    main()
