import os
import re
from dotenv import load_dotenv
import openai

load_dotenv()


class SentimentMarkup():

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.file_name = ''
        self.test_input_dir = os.path.join(
            os.getenv('INPUT_DIR'), os.getenv('TEST_INPUT_DIR'))
        self.output_dir = os.getenv('OUTPUT_DIR')

    def getFileName(self, filename):
        title = filename.split('/')[-1]
        return ''.join(title.split('.')[0])

    def processText(self, filename):
        if '.txt' in filename:
            try:
                self.file_name = self.getFileName(filename)
                with open(filename) as input:
                    txt = input.read()
                    paragraphs = txt.split('\n\n')
                    main_text = re.sub('[^A-Za-z0-9 .\"\n[]!]+', '', ''.join(
                        paragraphs)).replace('\n', ' ').replace(".\"", "\".").split('.')
                    main_text = [sentence+".".strip()
                                 for sentence in main_text]
                    if len(paragraphs) > 3:
                        title = paragraphs[0]
                        description = paragraphs[1].replace('\n', ' ')
                        main_text = re.sub('[^A-Za-z0-9 .\"\n[]]+', '', ''.join(
                            paragraphs[2:])).replace('\n', ' ').replace(".\"", "\".").split('.')
                        main_text = [sentence+".".strip()
                                     for sentence in main_text]
                        return [title] + [description] + main_text
                    return main_text
            except Exception as e:
                print("Kindly provide valid file path!\nERROR: ", e)
        else:
            print("Kindly provide a .txt file as input only.")

    def markupWithSentiments(self, text):
        final_text = ''
        sentiments = ['dislike', 'happy', 'neutral', 'excited']
        openai.api_key = self.api_key
        prompt = 'Classify the sentiment in this text and write "dislike", \
                                "happy", "neutral", or  "excited"\n\n'

        for sentence in text:
            if len(sentence) > 1:
                try:
                    response = openai.Completion.create(
                        model="text-davinci-002",
                        prompt=prompt + sentence,
                        temperature=0,
                        max_tokens=60,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0
                    )
                    sentiment = response["choices"][0]["text"].replace('"', "")

                    final_sentiment = ''.join(
                        [value for value in sentiment.split() if value in sentiments])
                    if final_sentiment == '' or len(final_sentiment) > 7:
                        final_sentiment = "neutral"
                    final_text += f"<{final_sentiment}>{sentence}\n"
                except Exception as e:
                    print("There was some error analysing the following sentence: ",
                          sentence, "\nERROR: ", e)

        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        with open(os.path.join(self.output_dir, self.file_name+"_output.txt"), "w") as output_file:
            output_file.write(final_text)

    def test_method(self):
        test_input_list = os.listdir(self.test_input_dir)
        for file in test_input_list:
            clean_text = self.processText(
                os.path.join(self.test_input_dir, file))
            self.markupWithSentiments(clean_text)


if __name__ == '__main__':

    input_file_path = 'input/JFKMoon_Speech.txt'

    markup_engine = SentimentMarkup()
    markup_engine.test_method()
    clean_input = markup_engine.processText(input_file_path)
    markup_engine.markupWithSentiments(clean_input)

