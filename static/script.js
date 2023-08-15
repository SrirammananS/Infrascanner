document.addEventListener("DOMContentLoaded", function () {
    console.log("entered EventListener js");
    const urlInput = document.querySelector('input[name="url"]');
    const testsslUrl = document.getElementById('testssl-url');
    const sslscanDomain = document.getElementById('sslscan-domain');
    const nmapDomain = document.getElementById('nmap-domain');
    const startScanButton = document.getElementById('startScanButton');
    const loadingSpinner = document.getElementById("loadingSpinner");
    const scanForm = document.getElementById('scanForm');




    urlInput.addEventListener('input', function () {
        const inputValue = urlInput.value;
        testsslUrl.innerText = inputValue;

        // Extract domain from URL
        const domain = new URL(inputValue).hostname;
        sslscanDomain.innerText = domain;
        nmapDomain.innerText = domain;

    });

    scanForm.addEventListener("submit", function () {
        loadingSpinner.style.display = "block"; // Show the spinner when the form is submitted
    });

});
document.getElementById('download-pdf').addEventListener('click', function () {
    // Fetch the necessary data (URL, testssl result, sslscan result, nmap result)
    const url = document.getElementById('urlElement').innerText;
    const testssl_result = document.querySelector('#testssl .custom-styling').innerHTML;
    const sslscan_result = document.querySelector('#sslscan .custom-styling').innerHTML;
    const nmap_result = document.querySelector('#nmap .custom-styling').innerHTML;
    console.log(url,testssl_result,sslscan_result,nmap_result);

    // Create a FormData object to send the data to the server
    const formData = new FormData();
    formData.append('url', url);
    formData.append('testssl_result', testssl_result);
    formData.append('sslscan_result', sslscan_result);
    formData.append('nmap_result', nmap_result);

    // Send a POST request to the server to generate and download the PDF report
    fetch('/generate_html', {
        method: 'POST',
        body: formData
    })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'scan_report.html';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a); // Remove the temporary <a> element
            window.URL.revokeObjectURL(url);
        });
});













