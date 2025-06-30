function updateUI(jsonData,endpoint) {
    // Extract the parent URL segment before the first '/' or '?' or end of string
    let parentUrl = endpoint.split(/[/?]/)[0];
    var gen_element = document.getElementById(parentUrl + '_gen')
    var con_element = document.getElementById(parentUrl + '_con')
    var bal_element = document.getElementById(parentUrl + '_bal')
    gen_element.innerHTML = Number(jsonData.generation_data).toFixed(2)
    con_element.innerHTML = Number(jsonData.consumption_data).toFixed(2)
    bal_element.innerHTML = Number(jsonData.generation_data - jsonData.consumption_data).toFixed(2)
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