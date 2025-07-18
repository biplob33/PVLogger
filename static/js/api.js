// Uses CountUp.js for number animation: https://inorganik.github.io/countUp.js/
// Add CountUp.js to your HTML: <script src="https://cdn.jsdelivr.net/npm/countup.js@2.8.0/dist/countUp.umd.js"></script>
function animateValue(element, start, end, duration) {
    if (!element) return;
    // Remove previous CountUp instance if exists
    if (element._countUpInstance) {
        element._countUpInstance.reset();
    }
    // Create new CountUp instance
    const countUp = new window.countUp.CountUp(element, end, {
        startVal: start,
        duration: duration / 1000, // CountUp uses seconds
        decimalPlaces: 2,
        separator: ','
    });
    element._countUpInstance = countUp;
    countUp.start();
}

function updateUI(jsonData, endpoint) {
    // Extract the parent URL segment before the first '/' or '?' or end of string
    let parentUrl = endpoint.split(/[/?]/)[0];
    var gen_element = document.getElementById(parentUrl + '_gen');
    var con_element = document.getElementById(parentUrl + '_con');
    var bal_element = document.getElementById(parentUrl + '_bal');
    // Animate values
    animateValue(gen_element, 0, Number(jsonData.generation_data), 600);
    animateValue(con_element, 0, Number(jsonData.consumption_data), 300);
    animateValue(bal_element, 0, Number(jsonData.generation_data - jsonData.consumption_data), 800);
}
function get_data(endpoint) {
    return fetch('/api/'+endpoint)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json().then(jsonData => {
                updateUI(jsonData, endpoint);
                return jsonData; // Return the data so it can be used in .then
            });
        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
        });
}
document.addEventListener('DOMContentLoaded', function() {
    // Replace 'your_endpoint_here' with the actual endpoint you want to fetch on page load
    const endpoint = 'yes/';
    get_data('yes/');
    get_data('mnth/');
    get_data('total/');

});