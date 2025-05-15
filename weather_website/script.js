/**
* @file scrip.js
*
* @brief This file contains useful function for handling data and managing website
*/

//function for switching to dark mode (purple)
/**
* @brief This function toggles between light and dark mode
*
* @details This fuction switches the website background between blue(light) and purple(dark)
*/
function toggleDarkMode() {
    document.body.classList.toggle("dark");
}

//function for hamburger functonality
/**
* @brief This function handles the navagation buttons
*
* @details This fuction allows the buttons at the top of the website to function
*/
function toggleMobileNav() {
    document.getElementById("nav-links").classList.toggle("show");
}

//function for calculating "feels like" temp
/**
* @brief This function calculates the "feels like" temp
*
* @param {number} tempF The temperature in ferinheight
* @param {number} humidity The humidity value
*
* @details This fuction completes calculations based on tempF and humidity to predict what the weather feels like
*/
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

//function for refreshing temp, humidity, and light data
/**
* @brief This function refreshes sensor data
*
* @details This fuction refreshes temps, humidity, and light data
*/
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
