### Loading Libs

library(tidytext)
library(dplyr)
library(tidyr)
library(stringr)
library(lubridate)
library(ggplot2)
library(reshape2)
library(wordcloud)

### Getting args

args <- commandArgs(trailingOnly = TRUE)
print(args[1])
ticker_file = toString(args[1])

 data_location <- sub(".csv", "", ticker_file)
 csv_sentiment_location <- paste0(data_location,"_sentiment.csv")
 pdf_location <- paste0(data_location,".pdf")
 pdf(file = pdf_location)
 

### Reading csv and tokenize

sample_file = 'data/apple_inc.csv'

df <- read.csv(ticker_file)

df <- df %>%
  group_by(date) %>%
  # Use unnest_tokens on a temporary column
  unnest_tokens(word, title, to_lower = TRUE, drop = FALSE) %>%
  # Separate the unnested words while keeping the original titles
  unnest(word) %>%
  # Ungroup the dataframe
  ungroup()




### Standardizing dates

standardize_dates <- function(date_str) {
  # Handle relative dates like '2 days ago', '1 week ago', '23 hours ago', etc.
  if (grepl("ago", date_str)) {
    num <- as.numeric(unlist(regmatches(date_str, regexpr("\\d+", date_str))))
    unit <- ifelse(grepl("day", date_str), "days", 
                   ifelse(grepl("week", date_str), "weeks",
                          ifelse(grepl("month", date_str), "months", 
                                 ifelse(grepl("hour", date_str), "hours", "years"))))
    standardized_date <- Sys.Date() - num * switch(unit, 
                                                   days = 1, 
                                                   weeks = 7, 
                                                   months = 30, 
                                                   hours = 1/24, 
                                                   years = 365)
  }
  # Handle full dates like 'Jun 26, 2023'
  else if (grepl(",", date_str)) {
    standardized_date <- as.Date(date_str, format="%b %d, %Y")
  }
  # Add more conditions as needed for other formats
  else {
    standardized_date <- as.Date(date_str) # assuming it's already in a standard format
  }
  return(format(standardized_date, "%Y-%m-%d")) # Ensure output is in 'YYYY-MM-DD' format
}

# Apply the function to your dataframe
df$standardized_date <- sapply(df$date, standardize_dates)

# Filter out dates more than 2 years ago
#df <- df %>%
#  filter(standardized_date > Sys.Date() - years(1) - months(2))

###  Filtering All Sentiments

bing <- get_sentiments("bing")


df_sentiment <- df %>%
  inner_join(bing) %>%
  count(index = standardized_date, word, sentiment) %>%
  spread(sentiment, n, fill = 0) %>%
  {print(.); .} %>% # This will print the data frame at this stage
  mutate(sentiment = positive - negative)


df_sentiment$index <- as.Date(df_sentiment$index, format = "%Y-%m-%d")

write.csv(df_sentiment, csv_sentiment_location , row.names=FALSE)


###  Creating Plot based on sentiments

ggplot(df_sentiment, aes(x = index, y = sentiment)) +
  geom_bar(stat = "identity", fill = ifelse(df_sentiment$sentiment >= 0, "blue", "red")) +
  theme_minimal() +
  labs(x = "Date", y = "Sentiment words", title = "Sentiment Over Time") +
  scale_x_date(date_breaks = "1 month", date_labels = "%b %Y") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

### Counting most common words on df

counting_words <- df %>%
  inner_join(bing) %>%
  count(word, sentiment, sort = TRUE)
head(counting_words)

### Plotting word count 

# counting_words %>%
#   mutate(n = ifelse(sentiment == "negative", -n, n)) %>%
#   mutate(word = reorder(word, n)) %>%
#   ggplot(aes(word, n, fill = sentiment))+
#   geom_col() +
#   coord_flip() +
#   labs(y = "Sentiment Score")

###  Word Cloud

# df %>%
#   inner_join(bing) %>%
#   count(word, sentiment, sort = TRUE) %>%
#   acast(word ~ sentiment, value.var = "n", fill = 0) %>%
#   comparison.cloud(colors = c("red", "dark green"),
#                    max.words = 100)
#  
 #sending all to pdf
 
dev.off()


