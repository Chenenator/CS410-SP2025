function toggleDarkMode() {
    document.body.classList.toggle("dark");
}

function toggleMobileNav() {
    document.getElementById("nav-links").classList.toggle("show");
}

function calculateFeelsLike(tempF, humidity) {
    if (tempF < 40 || humidity < 40) return tempF; // No adjustment needed

    const T = tempF;
    const R = humidity;
    const HI = -42.379 +
               2.04901523 * T +
               10.14333127 * R -
               0.22475541 * T * R -
               0.00683783 * T * T -
               0.05481717 * R * R +
               0.00122874 * T * T * R +
               0.00085282 * T * R * R -
               0.00000199 * T * T * R * R;

    return HI.toFixed(1);
}

async function refreshData() {
    const spinner = document.getElementById("spinner");
    spinner.classList.remove("hidden");

    try {
        const response = await fetch("weather_data.php");
        const data = await response.json();

        const tempF = parseFloat(data.TempF[0].value).toFixed(1);
        const tempC = parseFloat(data.TempC[0].value).toFixed(1);
        const humidity = parseFloat(data.Humidity[0].value).toFixed(0);
        const light = data.Brightness?.[0]?.value || "Unknown";
        const timestamp = new Date(parseInt(data.TempF[0].ts)).toLocaleTimeString();
        const feelsLike = calculateFeelsLike(tempF, humidity);

        document.getElementById("tempF").textContent = tempF;
        document.getElementById("tempC").textContent = tempC;
        document.getElementById("humidity").textContent = humidity;
        document.getElementById("light").textContent = light;
        document.getElementById("timestamp").textContent = timestamp;
        document.getElementById("feelsLike").textContent = feelsLike;

        // Automatically toggle dark mode based on light level
        if (light.toLowerCase() === "dim" || light.toLowerCase() === "dark") {
            document.body.classList.add("dark");
        } else {
            document.body.classList.remove("dark");
        }
    } catch (err) {
        console.error("Failed to fetch weather:", err);
        alert("❌ Could not fetch weather data.");
    } finally {
        spinner.classList.add("hidden");
    }
}

// Auto-refresh every 5 minutes
setInterval(refreshData, 300000); // 300000ms = 5min
window.onload = refreshData;
