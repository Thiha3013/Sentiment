# Sentiment Analysis

### Creates a bar graph that shows the public sentiment on a company across timeline. The program is also integrated with a local LLM which analyzes the data, interprets and summarizes it.

## How the program works 

The program scrapes the data from google news for the articles related to the ticker. Tidytext library is used to extract sentiment creates multiple relavent charts. The program uses a mistral language model to interpret the data and outputs the sentiments around the ticker and possible causes.

## To use the tool

WIP 

## Work in progess / Known issues

1. Implement mysql database to store created files
2. Create better prompt / finetune the AI to give better response
3. Filter some words while doing sentiment analysis that has no correlation with actual sentiment around the company
4. Improve GUI

