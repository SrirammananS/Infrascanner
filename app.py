from flask import Flask, render_template, request, Response, make_response
from bs4 import BeautifulSoup
from ansi2html import Ansi2HTMLConverter
import subprocess
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Create a thread pool for parallel execution
executor = ThreadPoolExecutor(max_workers=3)

@app.route('/', methods=['GET', 'POST'])
def index():
    default_testssl_options = ''  # Default TestSSL options
    default_sslscan_options = ''  # Default SSLScan options
    default_nmap_options = '-Pn -sT -sV -O -p0-65535' #--script http-methods,http-enum,ssl-dh-params,http-slowloris,ssl-enum-ciphers,http-iis-short-name-brute'

    if request.method == 'POST':
        url = request.form['url']
        testssl_options = default_testssl_options + \
            ' ' + request.form.get('testssl_options', '')
        sslscan_options = default_sslscan_options + \
            ' ' + request.form.get('sslscan_options', '')
        nmap_options = default_nmap_options + ' ' + \
            request.form.get('nmap_options', '')

        # testssl_result = run_testssl(testssl_options, url)
        # sslscan_result = run_sslscan(sslscan_options, get_domain(url))
        # nmap_result = run_nmap(nmap_options, get_domain(url))

        # Use the thread pool to run scans in parallel
        testssl_future = executor.submit(run_testssl, testssl_options, url)
        sslscan_future = executor.submit(
            run_sslscan, sslscan_options, get_domain(url))
        nmap_future = executor.submit(run_nmap, nmap_options, get_domain(url))

        # Wait for all scans to complete
        executor.shutdown(wait=True)

        testssl_result = testssl_future.result()
        sslscan_result = sslscan_future.result()
        nmap_result = nmap_future.result()

        # Convert ANSI codes to HTML for rendering
        converter = Ansi2HTMLConverter()
        testssl_result_html = converter.convert(testssl_result)
        sslscan_result_html = converter.convert(sslscan_result)
        nmap_result_html = converter.convert(nmap_result)

        return render_template('results.html',
                               url=url,
                               testssl_options=testssl_options,
                               sslscan_options=sslscan_options,
                               nmap_options=nmap_options,
                               testssl_result=testssl_result_html,
                               sslscan_result=sslscan_result_html,
                               nmap_result=nmap_result_html,
                               default_testssl_options=default_testssl_options,
                               default_sslscan_options=default_sslscan_options,
                               default_nmap_options=default_nmap_options)

    return render_template('index.html',
                           default_testssl_options=default_testssl_options,
                           default_sslscan_options=default_sslscan_options,
                           default_nmap_options=default_nmap_options)


def get_domain(url):
    domain = url.split('//')[-1].split('/')[0]
    return domain


def run_testssl(options, url):
    print("testssl", url, options)
    cmd = ['testssl', url]
    print(cmd)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def run_sslscan(options, domain):
    cmd = ['sslscan', options, domain]
    print(cmd)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def run_nmap(options, domain):
    cmd = ['nmap', options, domain]
    print(cmd)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


@app.route('/generate_html', methods=['POST'])
def generate_html():
    # Generate the HTML content
    html_content = render_template('results.html',
                                   url=request.form['url'],
                                   testssl_result=request.form['testssl_result'],
                                   sslscan_result=request.form['sslscan_result'],
                                   nmap_result=request.form['nmap_result'])

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find and remove the download button element
    download_button = soup.find('button', {'id': 'download-pdf'})
    if download_button:
        download_button.extract()

    # Modified HTML content without the download button
    modified_html = str(soup)

    # Create the response with modified HTML content
    response = make_response(modified_html)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = 'inline; filename=scan_report.html'

    return response


if __name__ == '__main__':
    app.run(debug=True)
