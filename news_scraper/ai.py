import pandas as pd
import sys
import nlpcloud
import subprocess
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
import os

api_key = "0ee96d65e6f16ad26427877b9d892d00d9945b5d"
api_key2 = "6e10cc0ee9c6ec43cc60169d6087020160ed96b2"
file_name1 = 'data/apple_inc_sentiment.csv'

def give_summary(file_name):
    df = pd.read_csv(file_name)

    key_dates = df['index'].unique()  # Assuming 'date' is a column in your dataframe
    summaries = []

    for date in key_dates:
        day_data = df[df['index'] == date]
        most_common_word = day_data['word'].value_counts().idxmax()
        overall_sentiment = 'positive' if day_data['sentiment'].sum() > 0 else 'negative'

        summary = f"On {date}, the most common sentiment word was '{most_common_word}' with an overall {overall_sentiment} sentiment. "
        summaries.append(summary)

    # Combine all summaries
    full_summary = ' '.join(summaries)
    
    return full_summary


def text_generation(file):
    company_name = file.replace("_sentiment.csv", "")
    company_name = company_name.replace("../data/", "")
    summary = give_summary(file)
    prompt =  f'''
    Please follow exactly the instructions:

    Read the summary below:

    {summary}
Structure your response to offer a clear, easy-to-follow narrative. Include the following elements:


Introduction:

Begin with an overview of the sentiment trend of the company {company_name} observed throughout the timeline.
Mention the variations in sentiment, indicating periods of positive and negative sentiments.

Monthly Sentiment Analysis:

For each month, identify the prevailing sentiment (positive or negative).
Extract and highlight the most frequently used sentiment words for each month.
Compare the sentiment of each month with the previous one, noting significant changes or consistencies.

In-depth Sentiment Shift Analysis:

Pinpoint months where there was a noteworthy shift in sentiment (e.g., from positive to negative or the opposite).
Delve into possible causes or events that might have triggered these shifts.
Provide an analysis of how these shifts correlate with specific events or general trends during that period.

Correlation with Notable Events:

Identify key events or news that align with substantial changes in sentiment.
Analyze the impact of these events on public perception and sentiment, discussing whether the sentiment change was a direct response to these events or influenced by broader factors.

Comprehensive Sentiment Overview:

Summarize the overall sentiment trajectory observed throughout the period.
Discuss any recurring themes or patterns in public sentiment, linking them to broader social, economic, or political contexts.
Conclude with a detailed analysis of the company's sentiment as the timeline end, including potential future implications based on past trends.

    '''


    client = nlpcloud.Client("finetuned-llama-2-70b", api_key, gpu=True)
    text = client.generation(
        prompt,
        max_length=4096,
        length_no_input=True,
        remove_input=True,
        end_sequence=None,
        top_p=1,
        temperature=0.8,
        top_k=5,
        repetition_penalty=1,
        num_beams=1,
        num_return_sequences=1,
        bad_words=None,
        remove_end_sequence=False
    )
    print(text['generated_text'])
    return text['generated_text']



def create_pdf_from_text(text, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    text_obj = c.beginText()
    text_obj.setTextOrigin(inch, 10 * inch)  # 1 inch from left and 10 inches from bottom (default top margin)
    text_obj.setFont("Times-Roman", 12)

    max_width = 540  # Maximum width of text line in points (7.5 inches)
    max_height = 10 * inch  # Maximum height for text before needing a new page

    lines = text.split('\n')
    for line in lines:
        # Split line into words
        words = line.split()
        line = ''

        for word in words:
            # Check if adding the next word exceeds the line width
            if c.stringWidth(line + word, "Times-Roman", 12) < max_width:
                line += word + ' '
            else:
                # Add current line to text object and start a new line
                text_obj.textLine(line)
                line = word + ' '

                # Check if we need a new page
                if text_obj.getY() <= 2 * inch:  # 2 inches from bottom
                    c.drawText(text_obj)
                    c.showPage()
                    text_obj = c.beginText()
                    text_obj.setTextOrigin(inch, 10 * inch)
                    text_obj.setFont("Times-Roman", 12)

        # Add the last line of the current paragraph
        text_obj.textLine(line)

    # Draw any remaining text
    c.drawText(text_obj)
    c.save()

def merge_pdfs(new_pdf, existing_pdf, output_pdf):
    pdf_writer = PdfWriter()
    
    # Append new PDF
    new_pdf_reader = PdfReader(new_pdf)
    for page in new_pdf_reader.pages:
        pdf_writer.add_page(page)
    
    # Append existing PDF
    existing_pdf_reader = PdfReader(existing_pdf)
    for page in existing_pdf_reader.pages:
        pdf_writer.add_page(page)

    # Write out the merged PDF
    with open(output_pdf, 'wb') as out_file:
        pdf_writer.write(out_file)

def remove_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print(f"The file {filename} does not exist.")


def open_pdf(file_path):
    if sys.platform == "win32":
        os.startfile(file_path)  # For Windows
    elif sys.platform == "darwin":
        subprocess.run(["open", file_path])  # For macOS
    else:
        subprocess.run(["xdg-open", file_path])


def main(file_name):

    text_string = text_generation(file_name)
    create_pdf_from_text(text_string, "new_pdf.pdf")
    existing_pdf =  file_name.replace("_sentiment.csv", ".pdf")
    merge_pdfs("new_pdf.pdf", existing_pdf, existing_pdf)
    remove_file("new_pdf.pdf")
    open_pdf(existing_pdf)
    print("file is sucessfully generated")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = str(sys.argv[1])     
        main(file_name)
    else:
        print("No ticker symbol provided")


