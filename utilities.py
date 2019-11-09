'''
Importer script for reading data from CSV, log, and JSON files and posting it to Elasticsearch
'''
import csv
import json
import os
import sys
import re
import requests

from nltk.util import everygrams

def process_report(args):
    es_mapping_fields, es_mapping_name = retrieve_es_mapping_fields(args.esIndex)
    try:
        csv_data = read_csv_data(args.csvFile)
    except IOError as error:
        sys.exit('I/O error({0}): {1} {2}'.format(error.errno, error.strerror, args.csvFile))

    bulk_row_data = ''
    row_count = 0
    create_action_string = '{"index": {}}'
    for row in csv_data:
        row_data = {}
        text_tokens = []
        for field in es_mapping_fields.keys():
            if es_mapping_fields[field]['type'] == 'text':
                text = row.get(field, None)
                row_data[field] = text
                if text:
                    stopwords_file = args.stopWordsFile
                    if stopwords_file:
                        stopwords = set(line.strip() for line in open(stopwords_file))
                        text_tokens = text.replace(':', ' ').replace(',', ' ').replace('.', ' ').replace(';', ' ').split()
                        good_tokens = []
                        for token in text_tokens:
                            if token not in stopwords and token.lower() not in stopwords:
                                good_tokens.append(token)
                        text_tokens = good_tokens
            elif 'Keywords' in field:
                ngram_keywords = []
                for length in range(1, 6):
                    ngram_keywords.append([])
                    for text_ngram in (list(everygrams(text_tokens, length, length))):
                        keyword = ''
                        for token in text_ngram:
                            keyword = '%s %s' % (keyword, token)
                        ngram_keywords[length - 1].append(keyword)
                row_data[field] = {}
                bigrams_field_name = "%sBigrams" % field
                trigrams_field_name = "%sTrigrams" % field
                fourgrams_field_name = "%sFourgrams" % field
                fivegrams_field_name = "%sFivegrams" % field
                row_data[field] = ngram_keywords[0]
                row_data[bigrams_field_name] = ngram_keywords[1]
                row_data[trigrams_field_name] = ngram_keywords[2]
                row_data[fourgrams_field_name] = ngram_keywords[3]
                row_data[fivegrams_field_name] = ngram_keywords[4]
                text_tokens = []
            else:
                row_data[field] = row.get(field, None)
        row_data_string = json.dumps(row_data)
        bulk_row_data = '%s\n%s\n%s\n' % (bulk_row_data, create_action_string, row_data_string)
        row_count += 1
        if row_count == 10000:
            print 'Sending 10000 records to Elasticsearch'
            send_data_to_elasticsearch(bulk_row_data, args.esIndex, es_mapping_name)
            bulk_row_data = ''
            row_count = 0
        
    send_data_to_elasticsearch(bulk_row_data, args.esIndex, es_mapping_name)
    
def send_data_to_elasticsearch(data, es_index, es_mapping_name):
    try:
        es_host = os.environ['ES_HOST']
    except KeyError:
        sys.exit('ES_HOST environment variable has not been defined.')
    post_request_url = 'http://%s:9200/%s/%s/_bulk' % (es_host, es_index, es_mapping_name)
    post_request = requests.post(post_request_url, headers={'Content-Type': 'application/x-ndjson'}, data=data)
    if(post_request.status_code == 200):
        print 'Current batch of data inserted successfully.'

def retrieve_es_mapping_fields(es_index):
    try:
        es_host = os.environ['ES_HOST']
    except KeyError:
        sys.exit('ES_HOST environment variable has not been defined.')
    mapping_request_url = 'http://%s:9200/%s/_mapping' % (es_host, es_index)
    mapping_request = requests.get(mapping_request_url)
    if(mapping_request.status_code == 404):
        error_message = 'Mapping for index %s could not be found.' % es_index
        sys.exit(error_message)
    elif(mapping_request.status_code != 200):
        error_message = 'There was some error when requesting the mapping.'
        sys.exit(error_message)
    else:
        es_mapping = mapping_request.json()[es_index]['mappings']
        es_mapping_name = es_mapping.keys()[0]
        es_mapping_fields = es_mapping[es_mapping.keys()[0]]['properties']
        return es_mapping_fields, es_mapping_name

def read_csv_data(csv_file_path):

    csv_file = open(csv_file_path, 'r')
    reader = csv.DictReader(csv_file)
    return reader

def process_log(args):
    log_file_path = args.logFile
    format_file_path = args.formatFile
    es_index = args.esIndex
    try:
        log_file = open(log_file_path, 'r')
    except IOError:
        file_not_found_message = 'No file found at %s. Please enter a valid file path.' % log_file_path
        sys.exit(file_not_found_message)
    try:
        format_file = open(format_file_path, 'r')
    except IOError:
        file_not_found_message = 'No file found at %s. Please enter a valid file path.' % format_file_path
        sys.exit(file_not_found_message)
    log_format = format_file.read()
    pattern = re.compile(log_format)
    parsed_lines = []
    for log_line in log_file:
        parsed_line = pattern.match(log_line)
        if parsed_line:
            parsed_lines.append(parsed_line.groupdict())
        else:
            print "Log line did not match pattern: %s" % log_line
        if len(parsed_lines) >= 1000:
            save_parsed_lines(parsed_lines, es_index)
            parsed_lines = []
    if len(parsed_lines) > 0:
        save_parsed_lines(parsed_lines, es_index)

def save_parsed_lines(parsed_lines, es_index):
    print "Saving batch of parsed lines."
    prepare_simple_json_bulk_import(parsed_lines, es_index, 'log_entry')

def process_json(args):
    json_file_path = args.jsonFile
    es_index = args.esIndex
    try:
        json_file = open(json_file_path, 'r')
    except IOError:
        file_not_found_message = 'No file found at %s. Please enter a valid file path.' % json_file_path
        sys.exit(file_not_found_message)
    json_data = json.load(json_file)
    save_json_data(json_data, es_index)

def save_json_data(json_data, es_index):
    print "Saving JSON data."
    prepare_simple_json_bulk_import(json_data, es_index, 'entry')

def prepare_simple_json_bulk_import(json_data, es_index, es_mapping):
    bulk_entry_string = ''
    create_action_string = '{"index": {}}'
    for entry in json_data:
        entry_data_string = json.dumps(entry)
        bulk_entry_string = '%s\n%s\n%s\n' % (bulk_entry_string, create_action_string, entry_data_string)
    send_data_to_elasticsearch(bulk_entry_string, es_index, es_mapping)