#Elasticsearch Import Script
##Introduction
This script provides a more convenient interface for getting data into [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html). The script was originally developed while researching Elasticsearch's potential uses for indexing various kinds of data. It was written to make the research more convenient and quicker; it was not ever intended to be a standalone project or product. The script may not be completely PEP8 or linted; however, maybe it will help someone else with importing data into Elasticsearch. :simple_smile:
##Requirements
The script requires Python. It was written in Python 2.7 (Sorry! Some workplaces have not made the jump to Python 3 yet.) and requires the excellent third-party libraries [requests](http://docs.python-requests.org/en/master/) and [Natural Language Toolkit](https://www.nltk.org/). This project does not provide a setup script at this time for installing these libraries.
###Elasticsearch
This script requires a running and reachable instance of Elasticsearch. Define the domain name or IP address for Elasticsearch as an environment variable called 'ES_HOST' before running the script. This can be done by either exporting the variable manually using the command line or by importing an environment file containing a declaration for ES_HOST.
##Usage
```
python elasticsearch-file-importer.py --help
usage: elasticsearch-file-importer.py [-h] {CSV,Logs,JSON} ...

Read a data from a variety of file formats and post the data to Elasticsearch

optional arguments:
  -h, --help       show this help message and exit

data_type:
  Supported data format

  {CSV,Logs,JSON}  Choose one of the supported data formats.
    CSV            Import a CSV file into Elasticsearch
    Logs           Import a log into ElasticSearch
    JSON           Import a JSON file into Elasticsearch
```
###CSV Files
When processing CSV files, the script first fetches the Elasticsearch mapping for the given index to determine which columns in the CSV file should be read and inserted into Elasticsearch documents. This functionality allows for only importing a subset of the columns from the CSV file instead of all of the columns. All of the columns can still be imported by defining an Elasticsearch index mapping with all of the columns.

**The Elasticsearch index mapping's field names must exactly match the names of the columns in the CSV file for the columns to be imported.**

The importer script will parse text fields into lists of keywords. The lists of keywords will be further analyzed using the [Natural Language Toolkit](https://www.nltk.org/) to generate bigrams, trigams, 4-grams, and 5-grams from the keywords. Bigrams, trigrams, 4-grams, and 5-grams are all kinds of n-grams. [n-grams](https://en.wikipedia.org/wiki/N-gram) are sequences of keywords that occur together in a given sample of text.

If a stopWordsFile argument is provided, the script will analyze the list of keywords for each text field and remove the words found in the stop words file. [Stop words](https://en.wikipedia.org/wiki/Stop_words) are usually extremely common words that are removed from samples of text to help improve identifying the most meaningful words in a sample of text. Filtering stop words in particular can improve the quality of [tag cloud visualizations](https://www.elastic.co/guide/en/kibana/current/tagcloud-chart.html), such as those found in [Kibana](https://www.elastic.co/guide/en/kibana/current/introduction.html).
```
python elasticsearch-file-importer.py CSV --help
usage: elasticsearch-file-importer.py CSV [-h] [--stopWordsFile STOPWORDSFILE]
                                          csvFile esIndex

positional arguments:
  csvFile               Path to the CSV file to read
  esIndex               Name of the Elasticsearch index mapping

optional arguments:
  -h, --help            show this help message and exit
  --stopWordsFile STOPWORDSFILE
                        Path to a file of stopwords
```
###Logs
The script will parse a log file line by line into JSON using a regular expression pattern to separate the components of the log format into named groups of characters. The regular expression pattern is defined in the first line of a separate file. An example of such a regular expression can be found in the regex-template.example file.
**When parsing logs, the script will not fetch the Elasticsearch index mapping first. The script will read the log file and attempt to post the data to the supplied Elasticsearch index. The index does not have to be defined before hand, but defining an index mapping can sometimes provide better results when searching or aggregating indexed data.**
```
python elasticsearch-file-importer.py Logs --help
usage: elasticsearch-file-importer.py Logs [-h] logFile formatFile esIndex

positional arguments:
  logFile     Path to the log file to read
  formatFile  Path to file containing log format regex string.
  esIndex     Name of the Elasticsearch index mapping

optional arguments:
  -h, --help  show this help message and exit
```
###JSON
The script will read a JSON file and post the data into Elasticsearch.
**When readiong JSON, the script will not fetch the Elasticsearch index mapping first. The script will read the JSON file and attempt to post the data to the supplied Elasticsearch index. The index does not have to be defined before hand, but defining an index mapping can sometimes provide better results when searching or aggregating indexed data.**
```
python elasticsearch-file-importer.py JSON --help
usage: elasticsearch-file-importer.py JSON [-h] jsonFile esIndex

positional arguments:
  jsonFile    Path to JSON file to read
  esIndex     Name of the Elasticsearch index mapping

optional arguments:
  -h, --help  show this help message and exit
```