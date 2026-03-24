// 1. Initialize the map
var map = L.map('map', { zoomControl: false }).setView([39.3331, -82.9824], 14);

// 2. Add Dark Matter tiles
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: 'SPAZZ Stealth Radar | &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 20
}).addTo(map);

let markers = {}; 

async function updateRadar() {
    try {
        console.log("📡 Fetching signals...");
        const response = await fetch('/api/users');
        const data = await response.json();
        
        const currentIds = new Set(data.map(u => u.id));
        const allCoords = [];

        data.forEach(user => {
            // Determine DNA color
            const color = user.wisp_class === 'whisp-red' ? '#ff0000' : 
                          (user.type === 'user' ? '#8a2be2' : '#00ffff');

            // If marker exists, update position smoothly
            if (markers[user.id]) {
                markers[user.id].setLatLng([user.lat, user.lon]);
            } else {
                // Create new neon marker
                markers[user.id] = L.circleMarker([user.lat, user.lon], {
                    radius: user.type === 'user' ? 10 : 7,
                    fillColor: color,
                    color: '#fff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8,
                    className: user.wisp_class || '' 
                }).addTo(map).bindPopup(`<b>${user.username}</b><br>${user.type}`);
            }
            // Add to the list for auto-zoom calculation
            allCoords.push([user.lat, user.lon]);
        });

        // 🧹 Cleanup: Remove markers for disconnected signals
        Object.keys(markers).forEach(id => {
            if (!currentIds.has(id)) {
                map.removeLayer(markers[id]);
                delete markers[id];
            }
        });

        // 📈 UI Update
        const statusEl = document.getElementById('status');
        if (statusEl) statusEl.innerText = `SIGNALS: ${data.length} LOCKED`;

        // 🎯 Auto-zoom (Triggers ONLY if we have markers and they move out of view)
        if (allCoords.length > 0) {
            const bounds = L.latLngBounds(allCoords);
            map.fitBounds(bounds, { padding: [100, 100], animate: true, maxZoom: 15 });
        }

    } catch (err) {
        console.error("⚠️ Radar Sync Error:", err);
    }
}

// Kickstart the engine
updateRadar();
setInterval(updateRadar, 3000);