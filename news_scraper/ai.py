import pandas as pd
import sys
import subprocess
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
import os
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp

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

    summary = give_summary(file)
    company_name = file.replace("_sentiment.csv", "")
    company_name = company_name.replace("data/", "")

    template =f"""summary: {summary}

    Response: Structure your response to offer a clear, easy-to-follow narrative. Include the following elements:

    Introduction:

    Start with an overview of the sentiment trend for {company_name} over the observed timeline.
    Highlight the variations in sentiment, identifying periods of positivity and negativity.


    Key Sentiment Shifts:

    Identify months with significant sentiment changes (e.g., from positive to negative).
    Investigate potential triggers for these shifts, considering relevant events or news.
    Explore the correlation between these shifts and specific occurrences or general trends at those times.

    Correlation with Key Events:

    Pinpoint major events or news coinciding with substantial sentiment changes.
    Discuss the impact of these events on the sentiment, analyzing if the change was a direct response or influenced by wider factors.
    
    Overall Sentiment Summary:

    Provide a summary of the sentiment trajectory over the period.
    Discuss any patterns or themes in sentiment, relating them to broader contexts.
    Conclude with an analysis of the current sentiment and potential future implications based on observed trends.
"""
    
    prompt = PromptTemplate.from_template(template)

    # Callbacks support token-wise streaming
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

    n_gpu_layers = -1  # The number of layers to put on the GPU. The rest will be on the CPU. If you don't know how many layers there are, you can use -1 to move all to GPU.
    n_batch = 512  # Should be between 1 and n_ctx, consider the amount of RAM of your Apple Silicon Chip.

    llm = LlamaCpp(
        model_path="/Users/tha/coding/projects/Sentiment/capybarahermes-2.5-mistral-7b.Q4_K_M.gguf",
        n_gpu_layers=n_gpu_layers,
        n_ctx=4096,
        n_batch=n_batch,
        f16_kv=True,  # MUST set to True, otherwise you will run into problem after a couple of calls
        callback_manager=callback_manager,
        max_tokens=4096,
        temperature=0,
        verbose=True,  # Verbose is required to pass to the callback manager
    )
    #summary1 = summary
    #response = llm_chain.invoke(summary)
    response = llm.invoke(template)


    return(response)


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

"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = str(sys.argv[1])     
        main(file_name)
    else:
        print("No ticker symbol provided")
"""
main(file_name1)

