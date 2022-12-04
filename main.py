import os
import io
import urllib.parse
import requests
from google.cloud import vision
import cohere
from dotenv import load_dotenv


load_dotenv()
# website: https://sincereley-darcy.unicornplatform.page/

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys.json"
cohere_api_key = os.getenv("cohere_api_key")
password = os.getenv("password")
co = cohere.Client(cohere_api_key)

# use google document AI to extract text from png
def extract_text_from_png(file_path):
    client = vision.ImageAnnotatorClient()
    with io.open(file_path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    document = response.full_text_annotation
    return document.text


def fix_grammar(text):
    end = text.split("\n")[-1]
    text = text.replace("\n", " ")
    prompt = (
        f"Please fix the grammar in the following letter.\n\nOriginal: {text}\n\nFixed:"
    )
    print(prompt)
    response = co.generate(
        model="xlarge",
        prompt=prompt,
        max_tokens=200,
        temperature=0.4,
        k=0,
        p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop_sequences=[end],
        return_likelihoods="NONE",
    )
    return response.generations[0].text


# generate response with cohere
def generate_response(text):
    preprompt = "Write a short letter in the style of an 18th century letter. Use at most 500 characters. Become the character Mr. Darcy from Pride and Prejudice. Please answer all the questions in the letter, and be sure to ask at least one question.\nLetter: "
    postprompt = "\n\nDarcy's Response:"
    prompt = preprompt + text + postprompt
    response = co.generate(
        model="xlarge",
        prompt=prompt,
        max_tokens=100,
        temperature=0.8,
        k=0,
        p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop_sequences=["Darcy"],
        return_likelihoods="NONE",
    )

    return response.generations[0].text


def send_card(message, address):
    base_url = "https://api.handwrytten.com/v1"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # send card to address
    order_url = base_url + "/orders/singleStepOrder"
    login = "kaiser@pister.dev"
    login = urllib.parse.quote(login)
    message = urllib.parse.quote(message)
    card_id = "70889"
    font_label = "Proper Jeff"
    credit_card_id = "39830"

    sender_name = "Pister Kaiser"
    sender_address1 = "20 Camino Del Diablo"
    sender_address2 = ""
    sender_city = "Orinda"
    sender_state = "CA"
    sender_zip = "94563"

    recipient_name = urllib.parse.quote(address["name"])
    recipient_address1 = urllib.parse.quote(address["address1"])
    recipient_address2 = urllib.parse.quote(address["address2"])
    recipient_city = urllib.parse.quote(address["city"])
    recipient_state = urllib.parse.quote(address["state"])
    recipient_zip = urllib.parse.quote(address["zip"])

    data = f"login={login}&password={password}&message={message}&card_id={card_id}&font_label={font_label}&credit_card_id={credit_card_id}&sender_name={sender_name}&sender_address1={sender_address1}&sender_address2={sender_address2}&sender_city={sender_city}&sender_state={sender_state}&sender_zip={sender_zip}&recipient_name={recipient_name}&recipient_address1={recipient_address1}&recipient_address2={recipient_address2}&recipient_city={recipient_city}&recipient_state={recipient_state}&recipient_zip={recipient_zip}"

    res = requests.post(order_url, data=data, headers=headers)
    return res


def load_address():
    address = {
        "name": "Kaiser Pister",
        "address1": "640 W. Wilson St.",
        "address2": "Unit 333",
        "city": "Madison",
        "state": "WI",
        "zip": "53703",
    }
    return address


def main():
    file_name = os.path.abspath("letter.jpg")
    note = extract_text_from_png(file_name)
    note = fix_grammar(note)
    print(note)
    message = generate_response(note)
    if len(message) > 500:
        message = message[:500]
    print(message)
    address = load_address()
    send_card(message, address)


if __name__ == "__main__":
    main()
