// Initialize the map
var map = L.map('map').setView([39.3331, -82.9824], 14);

// Add Dark Matter tiles
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: 'SPAZZ Stealth Radar'
}).addTo(map);

async function updateRadar() {
    try {
        console.log("Fetching signals...");
        const response = await fetch('/api/users');
        const data = await response.json();
        
        // Clear old markers if any
        map.eachLayer((layer) => {
            if (layer instanceof L.CircleMarker) {
                map.removeLayer(layer);
            }
        });

        const markers = [];

        data.forEach(user => {
            // Purple for real users, Cyan for Wisps
            const color = user.type === 'user' ? '#8a2be2' : '#00ffff';
            
            const marker = L.circleMarker([user.lat, user.lon], {
                radius: user.type === 'user' ? 10 : 6,
                fillColor: color,
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map).bindPopup(`<b>${user.username}</b><br>${user.type}`);
            
            markers.push([user.lat, user.lon]);
        });

        // Automatically zoom to fit everyone found
        if (markers.length > 0) {
            const bounds = L.latLngBounds(markers);
            map.fitBounds(bounds, { padding: [50, 50] });
        }

    } catch (err) {
        console.error("Radar Error:", err);
    }
}

// Initial pull
updateRadar();
// Refresh every 5 seconds to catch the "Heartbeat" moves
setInterval(updateRadar, 5000);
