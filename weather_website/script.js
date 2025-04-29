function toggleDarkMode() {
    document.body.classList.toggle("dark");
}

function toggleMobileNav() {
    document.getElementById("nav-links").classList.toggle("show");
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
        const timestamp = new Date(parseInt(data.TempF[0].ts)).toLocaleTimeString();

        document.getElementById("tempF").textContent = tempF;
        document.getElementById("tempC").textContent = tempC;
        document.getElementById("humidity").textContent = humidity;
        document.getElementById("timestamp").textContent = timestamp;
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

// Fetch brightness which was retrieved in back.js by logging in and making a request to ThingsBoard
function checkBrightness() {
  //fetch('http://localhost:3000/brightness') // Update to backend URL
  fetch('https://cs410sp2025.glitch.me/brightness')
    .then(res => res.json())
    .then(data => {
      if (data.brightness < 1300) {
        toggleDarkMode(); // turn on dark mode
      } else {
        document.body.classList.remove("dark"); // go back to default visuals
      }
    })
    .catch(
      err => {
        console.error("Brightness fetch failed:", err);
        alert("❌ Could not fetch brightness.");
      })
}

// Option 1: Run once on load, or refresh to update
checkBrightness();

// Option 2: Refresh brightness every 30 seconds
// setInterval(checkBrightness, 30000);