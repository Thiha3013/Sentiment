# Sentiment Analysis

### Creates a bar graph that shows the public sentiment on a company across timeline. The program is also integrated with a text-generation AI which infers the data on the graph and elaborates the data itself and events that might have happened during the timeline.

## How the program works 

The program scrapes data from google news of a chosen company using Python and supply the output a R program which performs sentiment analysis. This subsequent program outputs the chart that displays the sentiment around the company across a timeline. This data is then provided into a program that uses AI to infer and explain the sentiment data.

## To use the tool

1. git clone https://github.com/Thiha3013/Sentiment
2. run python app.py 
3. input any ticker on GUI to execute the program

## Work in progess / Known issues

1. Implement mysql database to store created files
2. Create better prompt / use more sophisticated AI to give better explanation
3. Filter some words while doing sentiment analysis that has no correlation with actual sentiment around the company
4. Improve GUI

