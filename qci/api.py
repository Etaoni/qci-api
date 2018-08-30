"""
Python 3 implementation of Qiagen Clinical Insight's API.

Installation:
    - Pipenv:
        pipenv install qci
    - Virtualenv:
        pip install qci
    - Pip:
        pip install qci
Usage:
    - Refer to the examples/ directory for examples
Notes:
    - Python 2 compatible
TODO:
    - multi-threading
    - check response codes
    - exception catching
    - DataPackage Class
"""
import requests
import os
import xmltodict
import tempfile
import sys

from datetime import datetime
from urllib.parse import urljoin
from multiprocessing.pool import ThreadPool

from qci.classes import DataPackage

BASE_URL = 'https://api.ingenuity.com/'


def get_access_token(client_id, client_secret):
    """
    :param client_id: QCI API key ID, can be found in https://apps.ingenuity.com/qcibridge/apiexplorer/
    :param client_secret: QCI API key secret, can be found in https://apps.ingenuity.com/qcibridge/apiexplorer/
    :return: access token str()
    """
    api_url = urljoin(BASE_URL, '/v1/oauth/access_token')

    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }
    resp = requests.get(api_url, params=payload)
    return resp.json()['access_token']


def validate_datapackage(datapackage):
    if not isinstance(datapackage, DataPackage):
        raise ValueError('DataPackage failed validation (not a DataPackage): {}'.format(datapackage))


def upload_datapackage(datapackage):
    """
    :param datapackage: qci.classes.DataPackage object
    :return:
    """
    api_url = urljoin(BASE_URL, '/v1/datapackages')

    # Validate the datapackage
    validate_datapackage(datapackage)

    # Securely generate the datapackage XML and write it to a file
    datapackage_fd, datapackage_file_path = tempfile.mkstemp(prefix='QCI_DP_', suffix='.zip')
    datapackage_fd.write(datapackage.to_xml())

    # POST the datapackage to QCI
    headers = {
        'Authorization': 'Bearer {}'.format(datapackage.access_token)
    }
    files = {'file': datapackage_fd.read()}
    resp = requests.post(api_url, headers=headers, files=files)
    """Example Response:
    {
      "method": "partner integration",
      "creator": "user1@domain.com",
      "users": ["user2@domain.com"],
      "title": "DM-121212 Cancer Hotspot Panel",
      "analysis-name": "DM-121212",
      "status": "PREPROCESSING",
      "stage": "Validating",
      "results-url": "https://api.ingenuity.com/datastream/analysisStatus.jsp?packageId=DP_727658804867835145738",
      "status-url": "https://api.ingenuity.com/v1/datapackages/DP_727658804867835145738",
      "pipeline-name": "QCI Somatic Cancer Pipeline",
      "percentage-complete": 20
    }
    """
    return resp.json()


def upload_datapackages(datapackages, debug=True):
    """
    :param datapackages: list( DataPackage ), example XML: https://developers.ingenuity.com/doc/clinical/Example__Somatic_Cancer_Diagnostic_Test.jsp#Example%3A_Somatic_Cancer_Metadata_Input_XML_File
    :param debug: set to True to receive debugging messages (tracebacks)
    :return:
    """
    if not debug:
        sys.tracebacklimit = 0  # Only show tracebacks when debugging

    # POST all of the datapackages
    qci_upload_pool = ThreadPool()
    qci_upload_pool.map(upload_datapackage, datapackages)
    qci_upload_pool.close()
    qci_upload_pool.join()


def check_submission_status(access_token, qci_id):
    """
    :param access_token: access token from get_access_token()
    :param qci_id: Either the datapackage ID or the accession-id of the sample
    :return: dict() containing the information on a submission
    """
    api_url = urljoin(BASE_URL, '/v1/datapackages/{}'.format(qci_id, access_token))  # either datapackage ID or accession-id
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    resp = requests.get(api_url, headers=headers)
    """Example Response:
    {
      "method":"partner integration",
      "creator":" user1@domain.com ",
      "users":[" user1@domain.com "],
      "title":"DM-121212 Cancer Hotspot Panel",
      "analysis-name":"DM121212",
      "status":"DONE",
      "stage":"Pipeline successfully completed",
      "results-url":"https://api.ingenuity.com/datastream/analysisStatus.jsp?packageId=DP_727658804867835145738",
      "status-url":"https://api.ingenuity.com/v1/datapackages/DP_727658804867835145738",
      "pipeline-name":"QCI Somatic Cancer Pipeline",
      "percentage-complete":100,"results-id":"491081",
      "results-redirect-url":"https://variants.ingenuity.com/vcs/?a=491081",
      "export-url":"https://api.ingenuity.com/v1/export/DP_727658804867835145738"
    }
    """
    return resp.json()


def get_report_pdf(access_token, qci_id, output_pdf_filename=''):
    """
    :param access_token: access token from get_access_token()
    :param qci_id: Either the datapackage ID or the accession-id of the sample
    :param output_pdf_filename: output name of the report .pdf, defaults to accession_id_date.pdf
    :return: output .pdf file path
    """
    api_url = urljoin(BASE_URL, '/v1/export/{}?'
                                'view={}'
                                '&access_token={}'.format(qci_id, 'pdf', access_token))  # either datapackage ID or accession-id
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    resp = requests.get(api_url, headers=headers)
    # Create default pdf filename
    if not output_pdf_filename:
        output_pdf_filename = '{}_{}.pdf'.format(qci_id, datetime.now().strftime('%Y-%m-%d'))
    # Write binary response to file
    with open(output_pdf_filename, 'wb') as report_pdf:
        report_pdf.write(resp.content)
    return os.path.abspath(output_pdf_filename)


def get_test_result_xml(access_token, qci_id):
    """
    :param access_token: access token from get_access_token()
    :param qci_id: Either the datapackage ID or the accession-id of the sample
    :return: dict() containing the result values for the test
    """
    api_url = urljoin(BASE_URL, '/v1/export/{}?'
                                'view={}'
                                '&access_token={}'.format(qci_id, 'reportXml', access_token))  # either datapackage ID or accession-id
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    resp_xml = requests.get(api_url, headers=headers).content
    resp_dict = xmltodict.parse(resp_xml)
    """Example Response:
    <report>
    <accession>DM-121212</accession>
    <age>45</age>
    <sex>male</sex>
    <ethnicity>African American</ethnicity>
    <patientName>******</patientName>
    <dateOfBirth>1967-08-05</dateOfBirth>
    <specimenId>14-375C</specimenId>
    <specimentBlock>1D</specimentBlock>
    <specimenCollectionDate>2014-03-19</specimenCollectionDate>
    <specimenDiagnosis>non-small cell lung cancer</specimenDiagnosis>
    <primaryTumorSite>lung</primaryTumorSite>
    <specimenType>biopsy</specimenType>
    <specimenDissection>manual</specimenDissection>
    <orderingPhysicianName>*******</orderingPhysicianName>
    <orderingPhysicianClient>RT44501</orderingPhysicianClient>
    <orderingPhysicianFacilityName>*******</orderingPhysicianFacilityName>
    <pathologistName>*********</pathologistName>
    <interpretation>Pathogenic</interpretation>
    <variant>
    <chromosome>11</chromosome>
    <position>108225575</position>
    <reference>C</reference>
    <alternate>T</alternate>
    <genotype>Het</genotype>
    <assessment>Pathogenic</assessment>
    <phenotype>non-small cell lung cancer</phenotype>
    <allelefraction>36</allelefraction>
    <gene>ATM</gene>
    """
    return resp_dict


def list_tests(access_token, state='', start_date='', end_date='', sort_by=''):
    """
    :param access_token: access token from get_access_token()
    :param state: state of the tests to list, choices: ('pending', 'in_review', 'needs_review', 'final')
    :param start_date: start date, inclusive, in yyyy-mm-dd format
    :param end_date: end date, inclusive, in yyyy-mm-dd format
    :param sort_by: how to sort the results, choices: ('receivedDateAsc', 'receivedDateDesc')
    :return: list( dict() ) of matching tests
    """
    api_url = urljoin(BASE_URL, '/v1/clinical?'
                                'state={}'.format(state))  # either datapackage ID or accession-id
    if start_date:
        api_url += '&startReceivedDate='+start_date
    if end_date:
        api_url += '&endReceivedDate='+end_date
    if sort_by:
        api_url += '&sort='+sort_by
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    resp = requests.get(api_url, headers=headers)
    """Example Response:
    [
      {
        "dataPackageID": "DP_746862303668038449347",
        "accessionID": "DM35335",
        "applicationUrl": "https://variants.ingenuity.com/vcs/view/analysis/532973",
        "exportUrl": "https://api.ingenuity.com/v1/export/DP_746862303668038449347",
        "state": "FINAL",
        "receivedDate": "2015-04-28"
      }
      {
        "dataPackageID": "DP_746862303668038449387",
        "accessionID": "DM36762",
        "applicationUrl": "https://variants.ingenuity.com/vcs/view/analysis/989931",
        "exportUrl": "https://api.ingenuity.com/v1/export/DP_746862303668038449387",
        "state": "FINAL",
        "receivedDate": "2015-04-29"
      }
      ...
    ]
    """
    return resp.json()


def share_test(access_token, qci_id, user_dict_list):
    """
    :param access_token: access token from get_access_token()
    :param qci_id: Either the datapackage ID or the accession-id of the sample
    :param user_dict_list: list( dict() ) of users to share a test with,
        example: [ {'email': 'alex@***.com'} ]
        docs: https://developers.ingenuity.com/doc/clinical/API_Endpoint_Reference_and_Examples.jsp#Share_Test_with_Others_API
    :return: HTTP response content
    """
    api_url = urljoin(BASE_URL, '/v1/datapackages/{}/users'.format(qci_id))  # either datapackage ID or accession-id
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    resp = requests.post(api_url, headers=headers, data=user_dict_list)
    return resp.content


def get_test_product_profiles(access_token):
    """
    :param access_token: access token from get_access_token()
    :param qci_id: Either the datapackage ID or the accession-id of the sample
    :return: HTTP response content
    """
    api_url = urljoin(BASE_URL, '/v1/testProductProfiles')  # either datapackage ID or accession-id
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    resp = requests.get(api_url, headers=headers)
    return resp.json()


if __name__ == '__main__':
    # TODO: move these to examples/
    import json
    qci_creds = json.loads(open('qci_credentials.json', 'r'))
    example_accession_id = '1807190065-COtA2477'

    auth_token = get_access_token(client_id=qci_creds['client_id'], client_secret=qci_creds['client_secret'])
    print('Got access token.')
    # print(check_submission_status(auth_token, '1807270053-COtA2682'))
    # print(get_test_result_xml(auth_token, '1807270053-COtA2682'))
    # print(list_tests(auth_token))
    print(list_tests(auth_token))

    # You would normally pull data from yous database here
    example_data_package = DataPackage(
        access_token=auth_token,
        primary_id='COtGx1234'
    )
    upload_datapackage(example_data_package)
